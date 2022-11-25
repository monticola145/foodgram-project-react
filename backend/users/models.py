from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Пользовательская модель User.
    email: электронная почта
    username: логин
    first_name: имя
    last_name: фамилия
    password: пароль
    """

    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICE = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Логин'
    )

    email = models.EmailField(
        max_length=150,
        unique=True,
        verbose_name='Электронная почта'
    )

    first_name = models.CharField(
        max_length=50, verbose_name='Имя', blank=True
    )

    last_name = models.CharField(
        max_length=50, verbose_name='Фамилия', blank=True
    )

    role = models.CharField(
        max_length=15,
        default=USER,
        choices=ROLE_CHOICE,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser


class Follow(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Избранный автор',
        related_name='following')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'