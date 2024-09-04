from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from .serializers import (SubscribeSerializer, SubscriptionSerializer,
                          UserAvatarUpdateSerializer, UserSerializer)

User = get_user_model()


class UserViewSet(UserViewSet):
    """
    Кастомный вьюсет для работы с пользователями.
    """
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """
        Создает подписку на другого пользователя.
        """
        current_user = request.user
        subscribed_to_user = get_object_or_404(User, id=id)

        data = {
            'user': current_user.id,
            'subscribed_to': subscribed_to_user.id
        }

        serializer = SubscribeSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """
        Удаляет подписку на другого пользователя.
        """
        current_user = request.user
        subscribed_to_user = get_object_or_404(User, id=id)
        delete_cnt, _ = Subscription.objects.filter(
            user=current_user, subscribed_to=subscribed_to_user
        ).delete()

        if delete_cnt > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request, pk=None):
        """
        Обработка PUT запроса для обновления аватара текущего пользователя.
        """
        user = request.user
        serializer = UserAvatarUpdateSerializer(
            user, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """
        Удаляет аватар пользователя.
        """
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения подписок текущего пользователя.
    """
    serializer_class = SubscriptionSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список подписок текущего пользователя.
        """
        return Subscription.objects.filter(user=self.request.user)
