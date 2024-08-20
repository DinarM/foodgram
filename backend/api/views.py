from rest_framework import viewsets

from .serializers import TagSerializer
from recipe.models import Tag

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()