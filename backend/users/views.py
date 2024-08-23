from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model

from .models import Subscription

from .serializers import (
    CustomUserSerializer, CustomUserCreateSerializer, SubscriptionSerializer,
    UserAvatarUpdateSerializer, CustomUserPasswordSerializer,
    SubscribeSerializer
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    Кастомный вьюсет для работы с пользователями.
    """
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        """
        Возвращает соответствующий сериализатор в зависимости от действия.
        """
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'set_password':
            return CustomUserPasswordSerializer
        return CustomUserSerializer

    @action(
        detail=True, methods=['post', 'delete'],
        url_path='subscribe', permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """
        Создает или удаляет подписку на другого пользователя.
        """
        current_user = request.user

        if not User.objects.filter(id=id).exists():
            return Response(
                {"detail": "Страница не найдена."},
                status=status.HTTP_404_NOT_FOUND
            )

        subscribed_to_user = User.objects.get(id=id)

        if request.method == 'POST':
            if current_user.id == int(id):
                return Response(
                    {"detail": "Нельзя подписаться на самого себя."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if Subscription.objects.filter(
                user=current_user, subscribed_to=subscribed_to_user
            ).exists():
                return Response(
                    {"detail": "Вы уже подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription = Subscription.objects.create(
                user=current_user,
                subscribed_to=subscribed_to_user
            )
            serializer = SubscribeSerializer(
                subscription, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                subscription = Subscription.objects.get(
                    user=current_user,
                    subscribed_to=subscribed_to_user
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Subscription.DoesNotExist:
                return Response(
                    {"detail": "Вы не подписаны на этого пользователя."},
                    status=status.HTTP_400_BAD_REQUEST
                )


class UserAvatarUpdateView(APIView):
    """
    Вьюсет для обновления и удаления аватара пользователя.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def put(self, request, *args, **kwargs):
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

    def delete(self, request, *args, **kwargs):
        """
        Обработка DELETE запроса для удаления аватара текущего пользователя.
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
