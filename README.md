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

DB_ENGINE=django.db.backends.postgresql (База данных)
DB_NAME= Название БД
POSTGRES_USER= Логин пользователя БД
POSTGRES_PASSWORD= Пароль пользователя БД
DB_HOST= Название хоста
DB_PORT= Порт


### Автор:

[Monticola]
Git - https://github.com/monticola
Email - ```jandiev2001@yandex.ru```

# The YAMDB Project

### Project description

Foodgram is a site designed for publishing recipes of various dishes. The functionality of the site includes publishing, modifying, adding to favorites and basket recipes, downloading the list of necessary products, subscribing to the authors.

### How to start a project:

Clone the repository and go to it on the command line:
```
git clone https://github.com/monticola/foodgram-project-react.git
```

Deploy Docker Containers:
```
docker-compose up
```

Perform migrations, build project statics, load ingredient list and tags:
```
docker-compose exec backend python manage.py migrate --run-syncdb
docker-compose exec backend python manage.py createsuperuser
docker-compose exec backend python manage.py collectstatic --no-input
docker-compose exec backend python manage.py load_data
```
### Technologies used

* PYTHON
* DJANGO
* DJANGO REST FRAMEWORK
* JWY


### API documentation

For API documentation please follow this link:

``http://localhost/redoc/``.

## API usage examples:

To retrieve an object, use:
``GET /api/{object}``.

To add a new object is used:
``POST /api/{object}``

### Template .env file

DB_ENGINE=django.db.backends.postgresql (Database)
DB_NAME= DB name
POSTGRES_USER= Username for the database
POSTGRES_PASSWORD= DB Username
DB_HOST= Host name
DB_PORT= Port


### Author:

[Monticola]
Git - https://github.com/monticola
Email - ``jandiev2001@yandex.ru``
