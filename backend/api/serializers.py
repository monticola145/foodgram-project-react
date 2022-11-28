import re

from django.core.validators import EmailValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from recipes.models import Tag, Ingredient, Recipe, RecipeIngredients
from djoser.serializers import UserSerializer
from rest_framework.serializers import ModelSerializer, ValidationError

User = get_user_model()


class AdminSerializer(ModelSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICE, default='user')

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name',
            'bio', 'role',
        )
        required_fields = ('username', 'email',)
        


class MyUserSerializer(UserSerializer):  # придумать крутое название
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'role')
        required_fields = ('username', 'email',)
        read_only_fields = ('role',)


class SignupSerializer(ModelSerializer):
    email = serializers.EmailField(
        validators=(
            UniqueValidator(queryset=User.objects.all()),
            EmailValidator()
        ),
        required=True
    )
    username = serializers.CharField(
        validators=(UniqueValidator(queryset=User.objects.all()),),
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, value):
        if value == 'me' or re.match(r'^[\w.@+-]+$', value) is None:
            raise ValidationError('Недопустимое имя пользователя')
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        fields = ('username', 'confirmation_code',)


class MyTagSerializer(ModelSerializer):  # придумать крутое название
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'colour',)


class MyIngredientSerializer(ModelSerializer):  # придумать крутое название
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class MyRecipeIngredients(ModelSerializer):

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class READINGMyRecipeSerializer(ModelSerializer):  # добавить сюда и в Model - Image
    author = MyUserSerializer(
        read_only=True
    )
    tags = MyTagSerializer(
        many=True,
    )
    ingredients = MyIngredientSerializer(
        many=True,
    )
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author',
                  'ingredients', 'description',
                  'tags', 'cooking_time'
                  )


class WRITINGMyRecipeSerializer(ModelSerializer):  # добавить сюда и в Model - Image
    author = MyUserSerializer(
        read_only=True
    )
    tags = MyTagSerializer(
        many=True,
    )
    ingredients = MyIngredientSerializer(
        many=True,
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'author',
                  'ingredients', 'description',
                  'tags', 'cooking_time'
                  )
