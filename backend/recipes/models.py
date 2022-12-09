from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):

    name = models.CharField(
        'Тег',
        max_length=settings.MAX_LENGTH_CHARFIELD_RECIPES,
        unique=True)
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=settings.MAX_LENGTH_COLOR)
    slug = models.SlugField(
        'Slug',
        max_length=settings.MAX_LENGTH_CHARFIELD_RECIPES,
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название ингредиента',
        max_length=settings.MAX_LENGTH_NAME)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.MAX_LENGTH_MEASURE)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id', 'name']
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient'),]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',)
    name = models.CharField(
        'Название рецепта',
        max_length=settings.MAX_LENGTH_NAME)
    image = models.ImageField(
        'Изображение',
        upload_to='recipes/')
    text = models.TextField(
        "Описание рецепта",
        help_text='Введите описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиент')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег')
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MaxValueValidator(
                settings.MAX_VALUE,
                message='Укажите корректное время приготовления'),
            MinValueValidator(
                settings.MIN_VALUE,
                message='Укажите корректное время приготовления')])
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='list_of_ingredients',
        verbose_name='Данный рецепт',)
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент для данного рецепта')
    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента',
        validators=[
            MinValueValidator(
                settings.MIN_VALUE,
                message='Укажите корректное количество ингредиента')])

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингрединеты для рецептов'

    def __str__(self):
        return f'{self.ingredient.name} {self.amount} {self.ingredient.measurement_unit}'


class AbstractModel(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт')

    class Meta:
        abstract = True


class Favourite(AbstractModel):

    class Meta(AbstractModel.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_in_favourite'),]

    def __str__(self):
        return f'{self.user}, рецепт {self.recipe} успешно добавлен в Избранное'


class ShoppingCart(AbstractModel):

    class Meta(AbstractModel.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_recipe_in_cart'),]

    def __str__(self):
        return f'{self.user}, рецепт {self.recipe} успешно добавлен в Корзину'
