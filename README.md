## Проект Продуктовый помощник. Дипломная работа.

Foodgram - проект, который позволяет польз0ователям просматривать рецепты, создавать их, подписываться на рецепты авторов, добавлять рецепты в избранное и в продуктовую корзину, откуда можно скачать список необходимых ингредиентов для добавленных в корзину рецептов.

Для испотзования перейдите: http://158.160.20.132/
Для доступа к админке:
http://158.160.20.132/
login: 1@1.com
password: admin

Позволяет работать с моделями базы:
- User (пользователи)
- Recipe (рецепт)
- Tag (теги)
- Ingredient (ингредиенты)
- Favorite (любимые рецепты)
- Сart (корзина)
- Subscription (подписка)

## Технологии в проекте
- Django, DRF, Docker, PostrgeSQL, NGINX

## Локальный запуск:
Скачайте репозиторийЖ
```
git@github.com:saminter22/foodgram-project-react.git
```

## Шаблон наполнения файла .env:
Создайте файл .env в папке infra/.env и заполните по шаблону с
указанием своего секретного ключа и пароля к БД:
```
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
POSTGRES_DB=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=secret # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
SECRET_KEY = 'secretkey' # секретный ключ (установите свой)
```
Или переименуйте файл .env.dev в .env и установите свойй пароль и ключ.

## Команды для установки и запуска проекта в контейнерах на локальном компьтере
Чтобы развернуть проект нужно зайти в папку с файлом docker-compose.yaml ( /infra ) и 
запустить контейнерную сборку командой:
```
docker-compose up -d --build
```
Для управления используйте команды (остановить/запустить/удалить):
```
docker-compose stop
docker-compose start
docker-compose down -v
```
Сделать первоначальные настройки проекта (миграции, статика) командой:
```
docker-compose exec web bash web-first-run.sh
```
Создайте суперюзера:
```
docker-compose exec web python manage.py createsuperuser
```
Авторизоваться в админке под суперюзером:
```
http://localhost/admin/
```
Корневая директория API:
```
http://localhost/api/
```
## Подробная документация
```
http://localhost/redoc/
```
### Автор проекта
Сергей Самойлов, 2023.
Saminter22
