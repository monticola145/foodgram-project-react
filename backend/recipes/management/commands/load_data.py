from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand
from recipes.models import Ingredient, Tag

ALREADY_EXISTS_IN_DATA_BASE = """
Данные уже загружены в БД! Если нужно загрузить их снова,
то удалите файл db.sqlite3, опосля запустите команду
'python manage.py migrate' чтобы создать новую пустую БД.
"""


class Command(BaseCommand):
    help = 'Загружает данные из ingredient.csv'

    def handle(self, *args, **options):
        
        if Tag.objects.exists():
            print('Данные Tags уже существуют!')
            print(ALREADY_EXISTS_IN_DATA_BASE)
            return
        print('Идёт загрузка данных Tags')
        for row in DictReader(open(
                f'{settings.BASE_DIR}\\data\\tags.csv',
                encoding='utf-8')):
            tags = Tag.objects.get_or_create(name=row['name'],
                        color=row['color'],
                        slug=row['slug'])

        if Ingredient.objects.exists():
            print('Данные Ingredient уже существуют!')
            print(ALREADY_EXISTS_IN_DATA_BASE)
            return
        print('Идёт загрузка данных Ingredient')
        for row in DictReader(open(
                f'{settings.BASE_DIR}\\data\\ingredients.csv',
                encoding='utf-8')):
            ingredient = Ingredient.objects.get_or_create(name=row['name'],
                                    measurement_unit=row['measurement_unit'])
        
        print('Загрузка завершена!')
