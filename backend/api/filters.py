from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe, Tag


class RecipesFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(method='check_if_favourited')
    is_in_shopping_cart = filters.BooleanFilter(method='check_if_in_cart')
    tags = filters.AllValuesMultipleFilter(queryset=Tag.objects.all(),
                                             field_name='tags__slug',
                                             to_field_name="slug")

    class Meta:
        model = Recipe
        fields = ('tags', 'is_favorited', 'is_in_shopping_cart')

    def check_if_favourited(self, queryset, name, value):
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def check_if_in_cart(self, queryset, name, value):
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientsFilter(filters.FilterSet):
    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)
