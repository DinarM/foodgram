import django_filters

from recipe.models import Recipe


class RecipeFilter(django_filters.FilterSet):
    """Фильтр для модели Recipe."""
    author = django_filters.NumberFilter(field_name='author__id')
    tags = django_filters.CharFilter(
        field_name='tags__slug', method='filter_by_tags'
    )
    is_favorited = django_filters.rest_framework.filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = django_filters.rest_framework.filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_by_tags(self, queryset, name, value):
        """Фильтрует рецепты по тегам."""
        tags = self.request.query_params.getlist('tags')
        return queryset.filter(tags__slug__in=tags).distinct()

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрует рецепты по статусу 'в избранном'."""
        print('включился')
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(favorites__user=user)
        return queryset.exclude(favorites__user=user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрует рецепты по статусу 'в корзине покупок'."""
        print('включился filter_is_in_shopping_cart')
        user = self.request.user
        if user.is_anonymous:
            return queryset
        if value:
            return queryset.filter(shopping_carts__user=user)
        return queryset.exclude(shopping_carts__user=user)
