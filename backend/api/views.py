import django_filters.rest_framework
from api.filters import IngredientsFilter, RecipesFilter
from api.pagination import MyPagination
from api.permissions import IsAdminOrReadOnly
from api.serializers import (CustomUserSerializer, FollowSerializer,
                             GetMyRecipeSerializer, MyIngredientSerializer,
                             MyTagSerializer, PostMyRecipeSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredients,
                            ShoppingCart, Tag)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import Follow, User

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
            get_object_or_404(
                Follow,
                user=request.user,
                author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['GET'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions',
        url_name='subscriptions',)
    def follows(self, request):
        '''Список подписок'''
        queryset = User.objects.filter(follower__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)


'''
Блок вьюсетов приложения recipes
'''


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = MyPagination
    serializer_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = RecipesFilter

    def get_serializer_class(self):
        if self.request.method not in SAFE_METHODS:
            return PostMyRecipeSerializer
        return GetMyRecipeSerializer

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        '''Добавить в избранное/убрать из избранного'''
        if Favourite.objects.filter(
            user=self.request.user,
            recipe=get_object_or_404(
                Recipe,
                id=pk)).exists():
            return Response(status=status.HTTP_201_CREATED)
        serializer = GetMyRecipeSerializer(
            get_object_or_404(Recipe, id=pk),
            context={'request': request})
        Favourite.objects.create(
            user=self.request.user,
            recipe=get_object_or_404(Recipe, id=pk))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete(
        detail=True,
        methods=['DELETE'],
        permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        get_object_or_404(
            Favourite,
            user=self.request.user,
            recipe=get_object_or_404(Recipe, id=pk)
            ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # тут подвис конкретно, доделаю в рамках второго ревью

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,),
        url_path='shopping_cart',
        url_name='shopping_cart',)
    def shopping_cart_management(self, request, pk):
        '''Добавить в избранное/убрать из корзины'''
    # тут подвис конкретно, доделаю в рамках второго ревью

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
        queryset = RecipeIngredients.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        text_to_print = 'Нужно купить:'
        return self.sending(queryset, text_to_print)
        # так?

    def sending(self, queryset, text_to_print):
        for product in queryset:
            text_to_print += (
                '\n' + str(Ingredient.objects.get(
                    id=product['ingredient']) + product['amount'] + product['measurement_unit']))

        response = HttpResponse(text_to_print, content_type="text/plain")
        response['Content-Disposition'] = (
            'attachment; filename=foodgram_products.txt')

        return response
        # так?


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = MyTagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None
    # так?


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = MyIngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    pagination_class = None
    # так?
    filterset_class = IngredientsFilter
