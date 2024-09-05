from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipe.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription

from .filters import IngredientFilter, RecipeFilter
from .pagination import CustomPageNumberPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeReadSerializer, RecipeWriteSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          SubscriptionSerializer, TagSerializer,
                          UserAvatarUpdateSerializer, UserSerializer)


User = get_user_model()


def redirect_to_recipe(request, short_code):
    """
    Перенаправляет на полный URL рецепта по короткому коду.
    """
    recipe = get_object_or_404(Recipe, short_code=short_code)
    return redirect(f'/recipes/{recipe.id}')


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
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для управления рецептами.
    """
    serializer_class = RecipeReadSerializer
    queryset = Recipe.objects.all()
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthorOrReadOnly]

    def get_serializer_class(self):
        """
        Возвращает сериализатор в зависимости от действия.
        """
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """
        Возвращает короткую ссылку на рецепт.
        """
        recipe = self.get_object()
        link = request.build_absolute_uri(f'/api/r/{recipe.short_code}')
        return Response({'short-link': link})

    @action(
        detail=True, methods=['post'],
        url_path='favorite', permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        """
        Добавляет рецепт в избранное.
        """
        recipe = self.get_object()

        data = {'recipe': recipe.id}

        serializer = FavoriteSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        """
        Удаляет рецепт из избранного.
        """
        recipe = self.get_object()
        current_user = request.user
        delete_cnt, _ = Favorite.objects.filter(
            user=current_user, recipe=recipe
        ).delete()

        if delete_cnt > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Данный рецепт не добавлен в избранное."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True, methods=['post'], url_path='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        """
        Добавляет рецепт в корзину покупок.
        """
        recipe = self.get_object()

        data = {'recipe': recipe.id}

        serializer = ShoppingCartSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        """
        Удаляет рецепт из корзины покупок.
        """
        recipe = self.get_object()
        current_user = request.user
        delete_cnt, _ = ShoppingCart.objects.filter(
            user=current_user, recipe=recipe
        ).delete()

        if delete_cnt > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Данный рецепт не добавлен в корзину."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False, methods=['get'],
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


class UserViewSet(UserViewSet):
    """
    Кастомный вьюсет для работы с пользователями.
    """
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    queryset = User.objects.all()

    @action(
        detail=True,
        methods=['post'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        """
        Создает подписку на другого пользователя.
        """
        current_user = request.user
        subscribed_to_user = get_object_or_404(User, id=id)

        data = {
            'user': current_user.id,
            'subscribed_to': subscribed_to_user.id
        }

        serializer = SubscribeSerializer(data=data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        """
        Удаляет подписку на другого пользователя.
        """
        current_user = request.user
        subscribed_to_user = get_object_or_404(User, id=id)
        delete_cnt, _ = Subscription.objects.filter(
            user=current_user, subscribed_to=subscribed_to_user
        ).delete()

        if delete_cnt > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['put'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request, pk=None):
        """
        Обработка PUT запроса для обновления аватара текущего пользователя.
        """
        user = request.user
        serializer = UserAvatarUpdateSerializer(
            user, data=request.data, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @avatar.mapping.delete
    def delete_avatar(self, request, pk=None):
        """
        Удаляет аватар пользователя.
        """
        user = request.user
        user.avatar = None
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Вьюсет для отображения подписок текущего пользователя.
    """
    serializer_class = SubscriptionSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Возвращает список подписок текущего пользователя.
        """
        return Subscription.objects.filter(user=self.request.user)
