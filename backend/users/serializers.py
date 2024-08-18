import re
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import Subscription

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
            'email', 'is_subscribed'
        )

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


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Subscription.
    """
    class Meta:
        model = Subscription
        fields = '__all__'
