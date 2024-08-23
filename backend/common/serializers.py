from rest_framework import serializers

from recipe.models import Recipe


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
