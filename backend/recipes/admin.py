from django.contrib import admin

from .models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)


class IngredientTabular(admin.TabularInline):
    model = Recipe.ingredients.through


class TagTabular(admin.TabularInline):
    model = Recipe.tags.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'id',
        'author', 'in_favourites',
        'list_of_ingredients',)
    list_filter = ('author', 'name',)
    readonly_fields = ('list_of_ingredients',)
    inlines = (IngredientTabular, TagTabular,)

    @staticmethod
    @admin.display(description='Количество в избранных')
    def in_favourites(obj):
        return obj.favorite.count()

    @admin.display(description='Список ингредиентов')
    def list_of_ingredients(self, obj):
        text_to_print = ''
        for ingredient in obj.ingredients.all():
            text_to_print += (' ' + ingredient.name + ',')
        return text_to_print[:-1]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(RecipeIngredients)
class RecipeIngredients(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe',)
    search_fields = ('user',)
    list_filter = ('user',)
