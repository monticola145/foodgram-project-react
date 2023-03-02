# Проект YAMDB

![Actions Status](https://github.com/monticola145/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)


### Описание проекта

Foodgram - это сайт, предназначенный для публикации рецептов различных блюд. В функционал сайта входит публикация, изменение, добавление в избранное и в корзину рецептов, скачивание списка необходимых продуктов, подписка на авторов.


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/monticola/foodgram-project-react.git
```


Развернуть Докер-контейнеры:
```
docker-compose up
```

Выполнить миграции, собрать статику проекта, загрузить список ингредиентов и тегов:
```
docker-compose exec backend python manage.py migrate --run-syncdb
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py load_data

```


### Используемые технологии

* PYTHON
* DJANGO
* DJANGO REST FRAMEWORK
* JWY


### Документация к API

Для ознакомления с документацией к API перейдите по ссылке:

```http://localhost/redoc/```

## Примеры использования API:

Для получения объекта используется:
```GET /api/{объект}```

Для добавления нового объекта используется:
```POST /api/{объект}```

### Шаблон .env файла

# База данных
DB_ENGINE=django.db.backends.postgresql
# Название БД
DB_NAME=
# Логин пользователя БД
POSTGRES_USER=
# Пароль пользователя БД
POSTGRES_PASSWORD=
# Название хоста
DB_HOST=
# Порт
DB_PORT=


### Автор:

[Monticola]
Git - https://github.com/monticola
Email - ```jandiev2001@yandex.ru```
