from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=settings.MAX_LENGTH_EMAILFIELD,
        unique=True,
        verbose_name='Электронная почта')
    username = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_USERS,
        unique=True,
        verbose_name='Логин')
    first_name = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_USERS,
        verbose_name='Имя',
        blank=True)
    last_name = models.CharField(
        max_length=settings.MAX_LENGTH_CHARFIELD_USERS,
        verbose_name='Фамилия',
        blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username


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
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='unique_follow'),
            models.CheckConstraint(
                name='self_follow_prevention',
                check=~models.Q(user=models.F('author')),
            ), ]
