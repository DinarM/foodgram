import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
# from django.core.exceptions import ValidationError
from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404

from .models import Subscription


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Кастомный сериализатор для отображения пользователя.
    Добавляет поле is_subscribed, которое указывает, подписан ли текущий
    пользователь на данного пользователя.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_subscribed', 'avatar'
        )
        read_only_fields = ('avatar',)

    def get_is_subscribed(self, obj):
        """
        Определяет, подписан ли текущий пользователь на данного пользователя.
        Возвращает True, если подписан, и False, если нет.
        """
        request = self.context.get('request')
        return (
            request 
            and request.user.is_authenticated 
            and Subscription.objects.filter(
            user=request.user, subscribed_to=obj
            ).exists()
        )


class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления аватара пользователя.
    """
    avatar = Base64ImageField(required=True, allow_null=True)

    class Meta:
        model = User
        fields = ('avatar',)

    def to_representation(self, instance):
        """
        Возвращает абсолютный URL для аватара пользователя.
        """
        representation = super().to_representation(instance)
        request = self.context.get('request')
        avatar_url = request.build_absolute_uri(instance.avatar.url)
        representation['avatar'] = avatar_url

        return representation


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.
    Отображает подписчиков пользователя.
    """
    follower = UserSerializer(
        source='subscribed_to', read_only=True
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('follower', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """
        Возвращает рецепты пользователя, на которого подписан.
        """
        from api.serializers import RecipeSimpleSerializer

        recipes = obj.subscribed_to.recipes.all()
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
                recipes = recipes[:recipes_limit]
            except ValueError:
                pass

        return RecipeSimpleSerializer(
            recipes, many=True, context=self.context
        ).data

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов пользователя.
        """
        return obj.subscribed_to.recipes.count()

    def to_representation(self, instance):
        """
        Изменяет структуру вывода.
        """
        user_data = UserSerializer(
            instance.subscribed_to, context=self.context
        ).data
        recipes = self.get_recipes(instance)
        user_data['recipes'] = recipes
        user_data['recipes_count'] = self.get_recipes_count(instance)
        return user_data


class SubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания и отображения подписок.
    """
    follower = UserSerializer(
        source='subscribed_to', read_only=True
    )
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Subscription
        fields = ('follower', 'recipes', 'recipes_count')

    def validate(self, data):
        """
        Проверка на уникальность подписки и само-подписку.
        """
        subscribed_to_user_id = self.initial_data.get('subscribed_to') 
        current_user = self.context['request'].user
        
        subscribed_to_user = get_object_or_404(User, id=subscribed_to_user_id)
        print(subscribed_to_user_id)
        if Subscription.objects.filter(user=current_user, subscribed_to=subscribed_to_user).exists():
            raise serializers.ValidationError(
                "Вы уже подписаны на этого пользователя."
            )
       
        if current_user.id == subscribed_to_user.id:
           raise serializers.ValidationError(
                "Нельзя подписаться на самого себя."
            )

        return data

    def create(self, validated_data):
        """Создание подписки."""
        current_user = self.context['request'].user
        subscribed_to_user_id = self.initial_data.get('subscribed_to')
        subscribed_to_user = get_object_or_404(User, id=subscribed_to_user_id)

        subscribe = Subscription.objects.create(
            user=current_user, subscribed_to=subscribed_to_user
        )

        return subscribe

    def to_representation(self, instance):
        """
        Возвращает данные рецепта в формате, подходящем для чтения.
        """
        return SubscriptionSerializer(instance, context=self.context).data
