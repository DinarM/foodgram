from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionViewSet,
                    TagViewSet, UserViewSet, redirect_to_recipe)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register(
    'users/subscriptions', SubscriptionViewSet, basename='subscriptions'
)
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('r/<str:short_code>/', redirect_to_recipe, name='redirect_to_recipe'),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
