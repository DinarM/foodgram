import re

from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Subscription
from api.helpers import Base64ImageField

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Кастомный сериализатор для создания пользователя.
    Добавляет валидацию для поля username.
    """
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'password'
        )

    def validate_username(self, value):
        """
        Проверка, что имя пользователя соответствует заданному регулярному
        выражению.
        """
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise ValidationError(
                "Имя пользователя может содержать только буквы, "
                "цифры и символы @/./+/-/_."
            )
        return value

    def validate(self, attrs):
        """
        Проверка, что все обязательные поля заполнены.
        """
        required_fields = [
            'username', 'first_name', 'last_name', 'email', 'password'
        ]
        for field in required_fields:
            if not attrs.get(field):
                raise serializers.ValidationError({
                    field: f"{field} является обязательным."
                })
        return super().validate(attrs)

class CustomUserPasswordSerializer(serializers.Serializer):
    """
    Сериализатор для изменения пароля пользователя.
    """
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_current_password(self, value):
        """
        Проверяет, что текущий пароль введен верно.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Текущий пароль неверен.")
        return value

    def validate_new_password(self, value):
        """
        Проверка нового пароля на соответствие стандартам безопасности
        и на отличие от текущего пароля.
        """
        user = self.context['request'].user
        if user.check_password(value):
            raise serializers.ValidationError("Новый пароль не должен соответствовать старому.")
        validate_password(value)
        return value

class CustomUserSerializer(UserSerializer):
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
        user = self.context.get('request').user
        if user.is_anonymous or user == obj:
            return False
        return Subscription.objects.filter(
            user=user, subscribed_to=obj
        ).exists()

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
    """
    class Meta:
        model = Subscription
        fields = '__all__'
