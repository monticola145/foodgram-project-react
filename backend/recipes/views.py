from rest_framework.viewsets import ModelViewSet

from models import Recipe
from pagination import StandardResultsSetPagination

from . import StandartResultSetPagination


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_lass = StandardResultsSetPagination
    serializer_class = None
    permission_classes = None
    filter_backends = None
    filterset_class = None

    def get_serializer_class(self):
        if self.request.methon in SAFE_METHODS:
            return None
        else:
            return None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
