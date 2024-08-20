from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import TagSerializer, IngredientSerializer
from recipe.models import Tag, Ingredient


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения тегов.
    """
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения ингредиентов.
    """
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
