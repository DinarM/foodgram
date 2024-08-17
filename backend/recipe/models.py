from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


def validate_positive_integer(value):
    """
    Валидатор для проверки, что значение больше нуля.
    Вызывает:
        ValidationError: Если значение меньше или равно 0.
    """
    if value <= 0:
        raise ValidationError(
            'Значение не может быть равно 0 или быть отрицательным.',
            params={'value': value},
        )


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


class CommonInfoBaseModel(models.Model):
    """
    Базовая модель с полем названия.
    """
    name = models.CharField(
        max_length=128,
        verbose_name='Название'
    )

    class Meta:
        abstract = True


class Ingredient(BaseModel, CommonInfoBaseModel):
    """
    Модель ингредиента.
    """
    measurement_unit = models.CharField(
        max_length=128,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(BaseModel, CommonInfoBaseModel):
    """
    Модель тега.
    """
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(BaseModel, CommonInfoBaseModel):
    """
    Модель рецепта.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='автор'
    )
    image = models.ImageField(
        upload_to='recipe/',
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
        validators=[validate_positive_integer]
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


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
        validators=[validate_positive_integer]
    )

    class Meta:
        verbose_name = 'ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} {self.amount} '
            f'добавлен в {self.recipe.name}'
        )


class Favorite(BaseModel):
    """
    Модель избранного.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в избранное {self.recipe.name}'


class ShoppingCart(BaseModel):
    """
    Модель корзины покупок.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_carts',
        verbose_name='пользователь'
    )

    class Meta:
        verbose_name = 'корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил в корзину {self.recipe.name}'
