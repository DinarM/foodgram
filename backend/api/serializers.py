from rest_framework import serializers

from recipe.models import Tag, Ingredient, Recipe, RecipeIngredient, Favorite
from users.serializers import CustomUserSerializer
from common.helpers import Base64ImageField
from common.serializers import RecipeSimpleSerializer


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


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецепта."""
    author = CustomUserSerializer(read_only=True)
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
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Возвращает True, если рецепт в корзине у пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.shopping_carts.filter(id=obj.id).exists()


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

        if not tags:
            raise serializers.ValidationError(
                "Нужно добавить хотя бы один тег."
            )
        if not ingredients:
            raise serializers.ValidationError(
                "Нужно добавить хотя бы один ингредиент."
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

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                id=ingredient_data['ingredient'].id
            )
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )

        return recipe

    def update(self, instance, validated_data):
        """Обновляет рецепт с новыми ингредиентами и тегами."""
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')

        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()

        instance.tags.set(tags_data)

        instance.recipe_ingredients.all().delete()
        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(
                id=ingredient_data['ingredient'].id
            )
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient,
                amount=ingredient_data['amount']
            )

        return instance

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

    def to_representation(self, instance):
        """
        Возвращает данные рецепта в формате, подходящем для чтения.
        """
        return RecipeSimpleSerializer(
            instance.recipe, context=self.context
        ).data
