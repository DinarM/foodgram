from django.db.models import Sum
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    TagSerializer, IngredientSerializer, RecipeReadSerializer,
    RecipeWriteSerializer, FavoriteSerializer, ShoppingCartSerializer
)
from recipe.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
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
    """
    Вьюсет для управления рецептами.
    """
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def update(self, request, *args, **kwargs):
        """
        Обновляет рецепт, если пользователь является автором.
        """
        instance = self.get_object()
        if instance.author != request.user:
            return Response(
                {'detail': 'Вы не можете обновлять чужие рецепты.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Удаляет рецепт, если пользователь является автором.
        """
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
        """
        Добавляет или удаляет рецепт из избранного.
        """
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

    @action(detail=True, methods=['post', 'delete'], url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из корзины покупок.
        """
        recipe = self.get_object()
        current_user = request.user

        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=current_user, recipe=recipe
            ).exists():
                return Response(
                    {"detail": "Вы уже добавили этот рецепт в корзину"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item = ShoppingCart.objects.create(
                user=current_user, recipe=recipe
            )
            serializer = ShoppingCartSerializer(
                cart_item, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            try:
                cart_item = ShoppingCart.objects.get(
                    user=current_user, recipe=recipe
                )
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response(
                    {"detail": "Данный рецепт не добавлен в корзину."},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """
        Создает и возвращает текстовый файл со списком покупок
        для текущего пользователя.
        """
        ingredients = Ingredient.objects.filter(
            recipes__shopping_carts__user=request.user
        ).values('name', 'measurement_unit').annotate(
            total_amount=Sum('recipes__recipe_ingredients__amount')
        )

        content = 'Список покупок:\n\n'
        for item in ingredients:
            content += (
                f"{item['name']} ({item['measurement_unit']}): "
                f"{item['total_amount']}\n"
            )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )

        return response
