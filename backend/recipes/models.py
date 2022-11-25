from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        'Тег',
        max_length=50,
        unique=True
    )

    colour = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=50
    )

    slug = models.SlugField(
        'Slug',
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

    amount = None  # привязка к другой БД
    measure = models.CharField(
        'Единица измерения',
        max_length=10
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id', 'name']

    def __str__(self):
        return self.name, self.measurement_unit


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

    # image = models.ImageField(
    #    'Изображение'
    # )

    description = models.TextField(
        "Описание рецепта",
        help_text='Введите описание рецепта')

    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Ингредиент'
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тег'
    )

    cooking_time = models.PositiveIntegerField(
        'Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('id',)

    def __str__(self):
        return self.name
