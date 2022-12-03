from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):

    name = models.CharField(
        'Тег',
        max_length=200,
        unique=True
    )

    colour = models.CharField(
        'Цветовой HEX-код',
        max_length=7
    )

    slug = models.SlugField(
        'Slug',
        max_length=200,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):

    name = models.CharField(
        'Название ингредиента',
        max_length=50
    )

    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=10
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id', 'name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Автор рецепта",
    )

    name = models.CharField(
        'Название рецепта',
        max_length=50
    )

    image = models.ImageField(
        'Изображение',
        upload_to='foodgram-project-react//backend//recipes//images'
    )

    text = models.TextField(
        "Описание рецепта",
        help_text='Введите описание рецепта')

    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        verbose_name='Ингредиент'
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тег'
    )

    cooking_time = models.PositiveIntegerField(  # в минутах?
        'Время приготовления'
    )

    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class ShoppingCart(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь')

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт в корзине')

    class Meta:
        verbose_name = 'Корзина'

    def __str__(self):
        return f'{self.user}, рецепт {self.recipe} успешно добавлен в Корзину'


class RecipeIngredients(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='list_of_ingredients',
        verbose_name='Данный рецепт',
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент для данного рецепта'
    )

    amount = models.PositiveSmallIntegerField(
        'Количество ингредиента'
    )

    class Meta:
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингрединеты для рецептов'

    def __str__(self):
        return f'{self.ingredient.name} {self.amount} {self.ingredient.measurement_unit}'  # молоко 500 мл


class Favourite(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь')

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранный рецепт')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user}, рецепт {self.recipe} успешно добавлен в Избранное'
