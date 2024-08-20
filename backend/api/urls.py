from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagViewSet


app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include(router.urls)),
]