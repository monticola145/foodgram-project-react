from csv import DictReader
from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient

ALREADY_EXISTS_IN_DATA_BASE = """
Данные уже загружены в БД! Если нужно загрузить их снова,
то удалите файл db.sqlite3, опосля запустите команду
'python manage.py migrate' чтобы создать новую пустую БД.
"""

class Command(BaseCommand):
    help = 'Загружает данные из ingredient.csv'

    def handle(self, *args, **options):

        if Ingredient.objects.exists():
            print('Данные Ingredient уже существуют!')
            print(ALREADY_EXISTS_IN_DATA_BASE)
            return

        print('Идёт загрузка данных category')

        for row in DictReader(open(
                f'{settings.BASE_DIR}\\data\\ingredients.csv',
                encoding='utf-8'
        )):
            ingredient = Ingredient(name=row['name'],
                                    measurement_unit=row['measurement_unit'])
            ingredient.save()