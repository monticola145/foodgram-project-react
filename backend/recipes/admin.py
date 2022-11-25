from django.contrib import admin

from .models import Ingredient, Recipe, RecipesIngredient, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author',)
    list_filter = ('author', 'name', 'tags',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measure',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'colour', 'slug',)


@admin.register(RecipesIngredient)
class RecipesIngredient(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)