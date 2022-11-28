from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
import django_filters.rest_framework


from api.pagination import MyPagination
from recipes.models import Ingredient, Recipe, Tag
from users.models import User

from api.permissions import IsAdmin, IsGuest, IsAdminOrReadOnly, CreateOrIsAuthorOrReadOnly
from api.serializers import (READINGMyRecipeSerializer, 
                             AdminSerializer, MyIngredientSerializer,
                             WRITINGMyRecipeSerializer, MyTagSerializer,
                             SignupSerializer, TokenSerializer, MyUserSerializer)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = MyUserSerializer

    @action(
        detail=True,
        methods=['GET', 'PATCH'],
        permission_classes=(IsAuthenticated,),
        url_path='me',
        url_name='me',
    )

    def me(self, request):

        if request.method == 'PATCH':
            serializer = MyUserSerializer(
                request.user, data=request.data,
                partial=True, context={'request': request}
            )
            serializer.is_valid()
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'GET':
            serializer = CustomUserSerializer(
            request.user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='follow',
        url_name='follow',
        
    )

    def follow(self, request, id):

        user = self.request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            Follow.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            following = get_object_or_404(
                Follow,
                user=user,
                author=author
            )
            following.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        



class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPagination
    serializer_class = None
    permission_classes = (CreateOrIsAuthorOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    #  filterset_class = None 

    def get_serializer_class(self):
        if not self.request.method in SAFE_METHODS:
            return WRITINGMyRecipeSerializer
        else:
            return READINGMyRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = MyTagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = MyIngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    #  filterset_class = None
