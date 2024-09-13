from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.crypto import get_random_string

from foodgram.constants import (INGREDIENT_MEASUREMENT_UNIT_SIZE,
                                INGREDIENT_NAME_SIZE, MAX_VALUE_VALIDATOR,
                                MIN_VALUE_VALIDATOR, RECIPE_NAME_SIZE,
                                RECIPE_SHORT_CODE_SIZE, TAG_NAME_SIZE,
                                TAG_SLUG_SIZE)

User = get_user_model()


class BaseModel(models.Model):
    """
    Базовая модель с полями даты создания и обновления.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Обновлено'
    )

    class Meta:
        abstract = True


class Ingredient(BaseModel):
    """
    Модель ингредиента.
    """
    name = models.CharField(
        max_length=INGREDIENT_NAME_SIZE,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=INGREDIENT_MEASUREMENT_UNIT_SIZE,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient_in_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(BaseModel):
    """
    Модель тега.
    """
    name = models.CharField(
        max_length=TAG_NAME_SIZE,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=TAG_SLUG_SIZE,
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name} ({self.slug})'


class Recipe(BaseModel):
    """
    Модель рецепта.
    """
    name = models.CharField(
        max_length=RECIPE_NAME_SIZE,
        verbose_name='Название'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор'
    )
    image = models.ImageField(
        upload_to='recipe/images',
        verbose_name='изображение'
    )
    text = models.TextField(
        verbose_name='текст'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='теги'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления',
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                message=(
                    f'Время не может быть меньше {MIN_VALUE_VALIDATOR}'
                )
            ),
            MaxValueValidator(
                MAX_VALUE_VALIDATOR,
                message=(
                    'Время приготовления не может превышать '
                    f'{MAX_VALUE_VALIDATOR} минут.'
                )
            )
        ]
    )
    short_code = models.CharField(
        max_length=RECIPE_SHORT_CODE_SIZE,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Короткий код'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name} by {self.author}'

    def generate_short_code(self):
        """Генерирует уникальный короткий код."""
        while True:
            short_code = get_random_string(length=10)
            if not Recipe.objects.filter(short_code=short_code).exists():
                return short_code

    def save(self, *args, **kwargs):
        """Переопределяем метод save для генерации короткого кода."""
        if not self.short_code:
            self.short_code = self.generate_short_code()
        super().save(*args, **kwargs)


class RecipeIngredient(BaseModel):
    """
    Модель ингредиента в рецепте.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество',
        validators=[
            MinValueValidator(
                MIN_VALUE_VALIDATOR,
                message=(
                    f'Количество не может быть меньше {MIN_VALUE_VALIDATOR}'
                )
            ),
            MaxValueValidator(
                MAX_VALUE_VALIDATOR,
                message=(
                    'Количество не может быть больше {MAX_VALUE_VALIDATOR}'
                )
            )
        ]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=('ingredient', 'recipe'),
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount} '
            f'добавлен в {self.recipe.name}'
        )


class UserRecipeBase(BaseModel):
    """
    Базовая модель для связи пользователя с рецептом.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} связан с {self.recipe.name}'


class Favorite(UserRecipeBase):
    """
    Модель избранного.
    """

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'favorites'
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe.name}'


class ShoppingCart(UserRecipeBase):
    """
    Модель корзины покупок.
    """

    class Meta(UserRecipeBase.Meta):
        default_related_name = 'shopping_carts'
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe.name}'
