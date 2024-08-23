from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    TagSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, FavoriteSerializer
)
from recipe.models import Tag, Ingredient, Recipe, Favorite
from .filters import RecipeFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения тегов."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для отображения ингредиентов."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для управления рецептами."""
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def update(self, request, *args, **kwargs):
        """Обновляет рецепт, если пользователь является автором."""
        instance = self.get_object()

        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете обновлять чужие рецепты.'},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете удалять чужие рецепты.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """
        Возвращает короткую ссылку на рецепт.
        """
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/recipes/{recipe.id}')
        return Response({'short-link': link})

    @action(detail=True, methods=['post', 'delete'], url_path='favorite')
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        current_user = request.user

        if request.method == 'POST':
            if Favorite.objects.filter(
                user=current_user, recipe=recipe
            ).exists():
                return Response(
                    {"detail": "Вы уже добавили этот рецепт в избранное"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.create(
                user=current_user, recipe=recipe
            )
            serializer = FavoriteSerializer(
                favorite, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                favorite = Favorite.objects.get(
                    user=current_user, recipe=recipe
                )
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Favorite.DoesNotExist:
                return Response(
                    {"detail": "Данный рецепт не добавлен в избранное."},
                    status=status.HTTP_400_BAD_REQUEST
                )
