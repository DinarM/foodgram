from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from django.contrib.auth import get_user_model

from .serializers import CustomUserSerializer, CustomUserCreateSerializer, UserAvatarUpdateSerializer, CustomUserPasswordSerializer

User = get_user_model()

class CustomUserViewSet(UserViewSet):
    """
    Кастомный ViewSet для работы с пользователями.
    Использует CustomUserSerializer для сериализации данных пользователей.
    """
    serializer_class = CustomUserSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия.

        Для создания пользователя возвращает CustomUserCreateSerializer, 
        для изменения пароля — CustomUserPasswordSerializer, 
        в остальных случаях — CustomUserSerializer.
        """
        if self.action == 'create':
            return CustomUserCreateSerializer
        elif self.action == 'set_password':
            return CustomUserPasswordSerializer
        return CustomUserSerializer
    

class UserAvatarUpdateView(APIView):
    """
    Вьюшка для обновления и удаления аватара пользователя.
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