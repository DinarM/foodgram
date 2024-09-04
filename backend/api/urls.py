from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
                    redirect_to_recipe)

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('r/<str:short_code>/', redirect_to_recipe, name='redirect_to_recipe'),
]
