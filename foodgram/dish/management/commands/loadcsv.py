"""Management-команда. Заполняет БД данными из csv-файлов.
Синтаксис:
python manage.py loadcsv csv_path model_name
"""

import csv

from django.apps import apps

from django.core.management.base import BaseCommand, CommandError

app_models = [model.__name__ for model in apps.get_models()]
set_csv_fields = ['name', 'measurement']


class Command(BaseCommand):
    help = 'Заполняет базу данных модели из файла csv.'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Путь к файлу csv.')
        parser.add_argument('model_name', type=str, help='Имя модели.')

    def handle(self, *args, **options):
        if options['model_name'] not in app_models:
            raise CommandError(
                f'Модели "{options["model_name"]}" нет в приложении.')
        model = apps.get_model(app_label='dish',
                               model_name=options['model_name'])
        try:
            with open(options['csv_path'], 'r', encoding="utf-8") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    model.objects.bulk_create([
                        model(name=row[0], measurement=row[1])
                    ])

        except FileNotFoundError:
            raise FileNotFoundError(
                f'Файл не найден или некорректный путь {options["csv_path"]}')

        # try:
        #     model.objects.bulk_create([
        #         model(
        #             **{rename_csv_fields.get(key) if rename_csv_fields.
        #             get(key) else key: value
        #                 for key, value in row.items()
        #             }) for row in incoming_data
        #     ])
        # except Exception as error:
        #     raise CommandError(
        #         f'Возникла ошибка при импорте данных в модель: {error}')

        # self.stdout.write (f'Данные из {options["csv_path"].split("/")[2]} '
        #         f'были успешно загружены в модель {options["model_name"]}')
        self.stdout.write('Данные загружены')
