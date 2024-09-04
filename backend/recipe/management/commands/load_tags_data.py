import csv

from django.core.management import BaseCommand
from recipe.models import Tag

ALREADY_LOADED_ERROR_MESSAGE = """
Если вам нужно перезагрузить данные о тегах из CSV файла,
сначала удалите файл db.sqlite3, чтобы уничтожить базу данных.
Затем выполните команду `python manage.py migrate`, чтобы создать
новую пустую базу данных с таблицами.
"""


class Command(BaseCommand):
    """
    Команда для загрузки данных из файла ../data/tags.csv
    в модель Tag.
    """
    help = "Загружает данные из ./data/tags.csv"

    def handle(self, *args, **options):
        """
        Выполняет загрузку данных из CSV файла в базу данных.
        """
        if Tag.objects.exists():
            print('Данные о тегах уже загружены... выход.')
            print(ALREADY_LOADED_ERROR_MESSAGE)
            return

        print("Загрузка данных о тегах")

        with open('./data/tags.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                name = row[0]
                slug = row[1]

                tag = Tag(name=name, slug=slug)
                tag.save()

        print("Данные успешно загружены.")
