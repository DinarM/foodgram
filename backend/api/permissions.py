from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение на обновление и удаление объекта только для его автора.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated


class UserPermission(BasePermission):
    """
    Разрешение для доступа к списку пользователей без аутентификации,
    но требующее аутентификацию для /users/me/.
    """
    def has_permission(self, request, view):
        if view.action == 'me':
            return request.user.is_authenticated
        return True
