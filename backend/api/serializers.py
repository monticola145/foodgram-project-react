from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.serializers import ModelSerializer, CharField, IntegerField, PrimaryKeyRelatedField
from rest_framework.fields import SerializerMethodField
from django.db.models import F

from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag, Favourite, ShoppingCart
from users.models import Follow

'''
Блок сериализаторов приложения users
'''
User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password',)


class CustomUserSerializer(UserSerializer):
    '''
    {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": false
    }
    '''
    is_subscribed = SerializerMethodField('check_subscribiton')
    # true/false в redoc, проверить

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name',
            'is_subscribed',
        )  # проверить в редоке порядок полей

    def check_subscribiton(self, obj):
        user = self.context.get('request').user
        if (self.context.get('request').user).is_anonymous:
            return False
        else:
            return Follow.objects.filter(user=user, author=obj).exists()
        # если падает с follow - это тут (is_anonymous - fix)


class FollowSerializer(CustomUserSerializer):
    '''
    {
        "email": "user@example.com",
        "id": 0,
        "username": "string",
        "first_name": "Вася",
        "last_name": "Пупкин",
        "is_subscribed": true,
        "recipes": [
            {
                "id": 0,
                "name": "string",
                "image": ".jpeg",
                "cooking_time": 1
            }
        ],
        "recipes_count": 0
    }
    '''
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

    def check_his_recipes(self, obj):  # recipes_limit применить (?)
        recipes_limit = (self.context.get('request')).GET.get('recipes_limit')
        recipes = (obj.recipes.all())[:recipes_limit]
        return (GetMyRecipeSerializer(recipes, many=True)).data

    def count_his_recipes(self, obj):
        return obj.recipes.count()


'''
Блок сериализаторов приложения recipes
'''


class MyTagSerializer(ModelSerializer):  # придумать крутое название
    class Meta:
        model = Tag
        fields = ('id', 'name', 'colour', 'slug',)


class MyIngredientSerializer(ModelSerializer):  # придумать крутое название
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)

class RecipeIngredientsSerializer(ModelSerializer):
    id = SerializerMethodField(
        'get_ingredient_id'
    )
    name = SerializerMethodField(
        'get_ingredient_name'
    )
    measurement_unit = SerializerMethodField(
        'get_ingredient_measurement_unit'
    )

    def get_ingredient_id(self, obj):
        return obj.ingredient.id

    def get_ingredient_name(self, obj):
        return obj.ingredient.name

    def get_ingredient_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class GetMyRecipeSerializer(ModelSerializer):  # добавить сюда и в Model - Image
    tags = MyTagSerializer(
        many=True,
    )
    author = CustomUserSerializer(
        read_only=True
    )
    ingredients = SerializerMethodField('get_ingredients_for_recipe')

    is_favorited = SerializerMethodField('check_if_favourited')

    is_in_shopping_chart = SerializerMethodField('check_if_in_chart')

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_chart', 
                  'name', 'image', 'text', 'cooking_time',
                  )
        # порядок как в редоке

    def get_ingredients_for_recipe(self, obj):
        ingredients = RecipeIngredients.objects.filter(recipe=obj)

        return RecipeIngredientsSerializer(ingredients, many=True).data   
        
    def check_if_favourited(self, obj):
        if (self.context.get('request').user).is_anonymous:
            return False
        else:
            return Favourite.objects.filter(recipe=obj).exists()
    
    def check_if_in_chart(self, obj):
        if (self.context.get('request').user).is_anonymous:
            return False
        else:
            return ShoppingCart.objects.filter(recipe=obj).exists()

class AddIngredientsToRecipe(ModelSerializer):
    id = IntegerField()
    amount = IntegerField()

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class PostMyRecipeSerializer(ModelSerializer):
    # redoc = ing, tag, img, name, text, cook
    ingredients = AddIngredientsToRecipe(many=True)

    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    image = Base64ImageField()

    name = CharField(max_length=200)

    text = CharField()

    cooking_time = IntegerField(validators=(MinValueValidator(1, message='>=1'),))
    # сформулировать нормальное требование
    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags',
                  'image', 'name',
                  'text', 'cooking_time',
                  )
