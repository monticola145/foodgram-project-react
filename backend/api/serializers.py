from django.core.validators import MinValueValidator
from django.db import IntegrityError
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField)

from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from users.models import User

'''
Блок сериализаторов приложения users
'''


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)


class CustomUserSerializer(UserSerializer):

    is_subscribed = SerializerMethodField('check_subscribiton')

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',)

    def check_subscribiton(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.follower.filter(author=obj).exists()


class FollowSerializer(CustomUserSerializer):

    recipes = SerializerMethodField('check_his_recipes')
    recipes_count = SerializerMethodField('count_his_recipes')

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'recipes',
            'recipes_count',
        )
        read_only_fields = ('first_name', 'last_name')

    def check_his_recipes(self, obj):
        request = self.context.get('request')
        if not request or self.context.get('request').user.is_anonymous:
            return False
        recipes_limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            recipes = (obj.recipes.all())[:int(recipes_limit)]
        return GetMyRecipeSerializer(recipes, many=True).data

    @staticmethod
    def count_his_recipes(obj):
        return obj.recipes.count()


'''
Блок сериализаторов приложения recipes
'''


class MyTagSerializer(ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class MyIngredientSerializer(ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientsSerializer(ModelSerializer):

    id = ReadOnlyField(
        source='ingredient.id')
    name = ReadOnlyField(
        source='ingredient.name')
    measurement_unit = ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class GetMyRecipeSerializer(ModelSerializer):
    tags = MyTagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = SerializerMethodField('get_ingredients_for_recipe')
    is_favorited = SerializerMethodField('check_if_favourited')
    is_in_shopping_chart = SerializerMethodField('check_if_in_chart')
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_chart',
                  'name', 'image', 'text', 'cooking_time',)

    def get_ingredients_for_recipe(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)

        return RecipeIngredientsSerializer(ingredients, many=True).data

    def check_if_favourited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()

    def check_if_in_chart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=obj).exists()


class AddIngredientsToRecipe(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class PostMyRecipeSerializer(ModelSerializer):
    ingredients = AddIngredientsToRecipe(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()
    cooking_time = IntegerField(validators=(
        MinValueValidator(
            1,
            message='Укажите корректное время приготовления'),))

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags',
                  'image', 'name',
                  'text', 'cooking_time',
                  )

    @staticmethod
    def get_ingredients(recipe=None, ingredients=None):
        for ingredient in ingredients:
            RecipeIngredients.objects.bulk_create(
                [RecipeIngredients(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(id=ingredient['id']),
                    amount=ingredient['amount']
                )])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            image=validated_data.pop('image'),
            text=validated_data.pop('text'),
            name=validated_data.pop('name'),
            **validated_data)
        self.get_ingredients(recipe, ingredients)
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        recipe = Recipe.objects.create(**validated_data)
        self.get_ingredients(recipe, ingredients)
        recipe.save()
        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetMyRecipeSerializer(instance, context=self.context).data


class FavouriteSerializer(ModelSerializer):

    class Meta:
        model = Favourite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favourite.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise IntegrityError('Рецепт уже добавлен в Избранное')
        return data

    def to_representation(self, instance):
        return GetMyRecipeSerializer(
            instance.recipe,
            context=self.context).data


class ShoppingCartSerializer(ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
            user=data.get('user'),
            recipe=data.get('recipe')
        ).exists():
            raise IntegrityError('Рецепт уже в корзине')
        return data

    def to_representation(self, instance):
        return GetMyRecipeSerializer(
            instance.recipe,
            context=self.context).data
