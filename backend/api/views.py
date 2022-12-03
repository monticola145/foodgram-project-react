import django_filters.rest_framework
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.pagination import MyPagination
from api.permissions import CreateOrIsAuthorOrReadOnly, IsAdminOrReadOnly
from api.serializers import (CustomUserSerializer, FollowSerializer,
                             GetMyRecipeSerializer, MyIngredientSerializer,
                             MyTagSerializer, PostMyRecipeSerializer)
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
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

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='favorite',
        url_name='favorite',)
    def add_to_favourite(self, request, pk):
        '''Добавить в избранное/убрать из избранного'''

        if self.request.method == 'POST':
            if Favourite.objects.filter(
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).exists():
                return Response(status=status.HTTP_201_CREATED)
            serializer = GetMyRecipeSerializer(
                get_object_or_404(Recipe, id=pk),
                context={'request': request}
            )
            Favourite.objects.create(
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            (get_object_or_404(
                Favourite,
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            )).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',)
    def shopping_cart_management(self, request, pk):
        '''Добавить в избранное/убрать из корзины'''

        if self.request.method == 'POST':
            if ShoppingCart.objects.filter(
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).exists():
                return Response(status=status.HTTP_201_CREATED)
            serializer = GetMyRecipeSerializer(
                get_object_or_404(Recipe, id=pk),
                context={'request': request}
            )
            ShoppingCart.objects.create(
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            (get_object_or_404(
                ShoppingCart,
                user=self.request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            )).delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',)
    def download_shopping_cart(self, request):
        recipes = []
        for recipe in ShoppingCart.objects.filter(user=self.request.user):
            recipes.append(recipe.recipe.id)
        products = RecipeIngredients.objects.filter(recipe__in=recipes).values(
            'ingredient').annotate(amount=Sum('amount'))

        text_to_print = 'Нужно купить:'
        for product in products:
            text_to_print += (
                '\n' + str(Ingredient.objects.get(
                    id=product['ingredient']) + product['amount'] + product['measurement_unit']))

        response = HttpResponse(text_to_print, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=foodgram_products.txt')

        return response


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = MyTagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = MyIngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
