from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, SubscriptionViewSet


app_name = 'users'

router = DefaultRouter()
router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
