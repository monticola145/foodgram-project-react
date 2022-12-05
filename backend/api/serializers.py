from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (CharField, IntegerField,
                                        ModelSerializer,
                                        PrimaryKeyRelatedField, ReadOnlyField)
from users.models import Follow, User
from django.shortcuts import get_object_or_404

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
        # ...нужно получать request... - это как в строке ниже или (self, request)?
        request = self.context.get('request')
        if request.user.is_anonymous or request is None:
            # ...Нужно проверить, что request нет... - в смысле None (как я сделал)?
            return False
        return Follow.objects.select_related('author').exists()
        # так?


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
        )  # проверить в редоке порядок полей
        read_only_fields = ('email', 'username')

    def check_his_recipes(self, obj):
        # ...нужно получать request... - это как в строке ниже или (self, request)?
        queryset = self.context.get('request')
        if (self.context.get('request').user).is_anonymous or (self.context.get('request')) is None:
            return False
        recipes_limit = queryset.GET.get('recipes_limit')
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
        fields = ('id', 'name', 'colour', 'slug',)


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

    def get_ingredient_id(self, obj):
        return obj.ingredient.id

    def get_ingredient_name(self, obj):
        return obj.ingredient.name

    def get_ingredient_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

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
        if (self.context.get('request').user).is_anonymous or (self.context.get('request')) is None:
            return False
        # return Favourite.objects.filter(user=user, recipe=obj).exists()
        # такой должен был быть фильтр?
        # return Favourite.objects.select_related('user').exists()
        # так или
        return Favourite.objects.select_related('recipe').exists()
        # так?

    def check_if_in_chart(self, obj):
        if (self.context.get('request').user).is_anonymous or (self.context.get('request')) is None:
            return False
        # return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        # такой должен был быть фильтр?
        # return ShoppingCart.objects.select_related('user').exists()
        # так или
        return ShoppingCart.objects.select_related('recipe').exists()
        # так?


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
    name = CharField(max_length=200)
    text = CharField()
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

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipes = []
        for ingredient in ingredients:
            recipes.append(RecipeIngredients.objects.create(
                recipe=Recipe.objects.create(**validated_data),
                ingredient_id=get_object_or_404(
                    Ingredient,
                    id=ingredient['id']),
                amount=ingredient['amount']))
        tags = validated_data.pop('tags')
        for recipe in recipes:
            recipe.tags.set(tags)

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        for ingredient in ingredients:
            RecipeIngredients.objects.create(
                recipe=instance,
                ingredient_id=get_object_or_404(
                    Ingredient,
                    id=ingredient['id']),
                amount=ingredient['amount'])
        tags = validated_data.pop('tags')
        instance.tags.set(tags)

        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return GetMyRecipeSerializer(instance, context=self.context).data
