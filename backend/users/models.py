from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q

from foodgram.constants import USER_USERNAME_SIZE, USER_NAME_SIZE


class BaseModel(models.Model):
    """
    Базовая модель с полями даты создания и обновления.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    """
    Модель пользователя.
    """
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=USER_USERNAME_SIZE,
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        max_length=USER_NAME_SIZE,
        blank=False,
        null=False
    )
    last_name = models.CharField(
        max_length=USER_NAME_SIZE,
        blank=False,
        null=False
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        verbose_name='аватар',
        blank=True,
        null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.email} ({self.username})'


class Subscription(BaseModel):
    """
    Модель подписки.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='пользователь'
    )
    subscribed_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='автор, на которого подписались'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'subscribed_to'),
                name='unique_subscription'
            ),
            CheckConstraint(
                check=~Q(user=F('subscribed_to')),
                name='user_cannot_subscribe_to_self'
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.subscribed_to}'
