from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet, UserAvatarUpdateView, SubscriptionViewSet


app_name = 'users'

router = DefaultRouter()
router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'users/me/avatar/', UserAvatarUpdateView.as_view(),
        name='user-avatar-update'
    ),
]
