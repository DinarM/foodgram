from djoser.views import UserViewSet
from .serializers import CustomUserSerializer


class CustomUserViewSet(UserViewSet):
    """
    Кастомный ViewSet для работы с пользователями.
    Использует CustomUserSerializer для сериализации данных пользователей.
    """
    serializer_class = CustomUserSerializer

    def get_serializer_class(self):
        """
        Возвращает кастомный сериализатор для всех действий в данном ViewSet.
        """
        return CustomUserSerializer
