from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                           ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Tag."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Ingredient."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения ингредиента и его количества в рецепте."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSimpleSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого отображения рецептов.
    """
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        """
        Возвращает абсолютный URL для изображения рецепта.
        """
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients', read_only=True, many=True
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'text', 'cooking_time', 'author', 'tags',
            'ingredients', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Возвращает True, если рецепт в избранном у пользователя."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """Возвращает True, если рецепт в корзине у пользователя."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and request.user.shopping_carts.filter(user=request.user, recipe=obj).exists()
        )


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для записи рецепта."""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients', 'tags', 'image', 'name', 'text', 'cooking_time'
        )

    def validate(self, data):
        """
        Проверка на наличие дубликатов и пустых списков тегов и ингредиентов.
        """
        tags = data.get('tags')
        ingredients = data.get('ingredients')
        image = data.get('image')

        if not tags:
            raise serializers.ValidationError(
                "Нужно добавить хотя бы один тег."
            )
        if not ingredients:
            raise serializers.ValidationError(
                "Нужно добавить хотя бы один ингредиент."
            )
        if not image:
            raise serializers.ValidationError(
                "Нужно добавить изображение рецепта."
            )

        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                "Теги не должны дублироваться."
            )

        ingredient_ids = [item['ingredient'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                "Ингредиенты не должны дублироваться."
            )

        return data

    def create(self, validated_data):
        """Создает рецепт с указанными ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        request = self.context.get('request')
        validated_data['author'] = request.user

        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        self.create_ingredients(recipe, ingredients_data)

        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт с новыми ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        super().update(instance, validated_data)

        instance.tags.set(tags_data)

        instance.ingredients.clear()
        self.create_ingredients(instance, ingredients_data)

        return instance

    def create_ingredients(self, recipe, ingredients_data):
        """Создает ингредиенты для рецепта."""
        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            recipe_ingredient = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            recipe_ingredients.append(recipe_ingredient)

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        """
        Возвращает данные рецепта в формате, подходящем для чтения.
        """
        return RecipeReadSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Favorite.
    """
    recipe = RecipeSimpleSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ('recipe',)

    def validate(self, data):
        """
        Проверка на наличие дубликатов рецептов в избранном.
        """
        recipe_id = self.initial_data.get('recipe')
        user = self.context['request'].user

        recipe = get_object_or_404(Recipe, id=recipe_id)

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "Вы уже добавили этот рецепт в избранное"
            )

        data['recipe'] = recipe
        return data

    def create(self, validated_data):
        """Добавляем рецепт в избранное."""
        user = self.context['request'].user
        recipe = validated_data['recipe']

        favorite = Favorite.objects.create(
            user=user, recipe=recipe
        )

        return favorite

    def to_representation(self, instance):
        """
        Возвращает данные рецепта в формате, подходящем для чтения.
        """
        return RecipeSimpleSerializer(
            instance.recipe, context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ShoppingCart.
    """
    recipe = RecipeSimpleSerializer(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('recipe',)

    def validate(self, data):
        """
        Проверка на наличие дубликатов рецептов в корзине.
        """
        recipe_id = self.initial_data.get('recipe')
        user = self.context['request'].user

        recipe = get_object_or_404(Recipe, id=recipe_id)

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "Вы уже добавили этот рецепт в корзину"
            )

        data['recipe'] = recipe
        return data

    def create(self, validated_data):
        """Добавляем рецепт в корзину."""
        user = self.context['request'].user
        recipe = validated_data['recipe']

        shopping_cart = ShoppingCart.objects.create(
            user=user, recipe=recipe
        )

        return shopping_cart

    def to_representation(self, instance):
        """
        Возвращает данные рецепта в формате, подходящем для чтения.
        """
        return RecipeSimpleSerializer(
            instance.recipe, context=self.context
        ).data
