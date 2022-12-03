import django_filters.rest_framework
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (SAFE_METHODS, IsAuthenticated,)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from api.pagination import MyPagination
from api.permissions import (CreateOrIsAuthorOrReadOnly, IsAdminOrReadOnly)
from api.serializers import (CustomUserSerializer, FollowSerializer,
                             MyIngredientSerializer, MyTagSerializer,
                             GetMyRecipeSerializer,
                             PostMyRecipeSerializer)
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow

User = get_user_model()


'''
Блок вьюсетов приложения users
'''


class CustomUserViewSet(UserViewSet):

    pagination_class = MyPagination
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe',)
    def follow(self, request, id):
        '''Подписка/отписка'''
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(author,
                                          data=request.data,
                                          context={"request": request})
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            follow = get_object_or_404(Follow,
                                       user=request.user,
                                       author=author)
            follow.delete()
            # при подписке на себя - get() returned more than one Follow, пофиксить
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        url_name='subscriptions',)
    def follows(self, request):
        '''Список подписок'''
        queryset = User.objects.filter(subscribing__user=request.user)
        serializer = FollowSerializer(queryset,
                                      many=True,
                                      context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


'''
Блок вьюсетов приложения recipes
'''


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPagination
    serializer_class = None
    permission_classes = (CreateOrIsAuthorOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return PostMyRecipeSerializer
        else:
            return GetMyRecipeSerializer

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
