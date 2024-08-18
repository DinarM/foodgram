from rest_framework.permissions import BasePermission


class CustomUserPermission(BasePermission):
    """
    Разрешение для доступа к списку пользователей без аутентификации,
    но требующее аутентификацию для /users/me/.
    """
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return True
