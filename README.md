# praktikum_new_diplom

## Учебный проект Продуктовый помощник. Дипломная работа.

Адрес проекта:
http://158.160.20.132/
login: admin1
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
Сделать первоначальные настройки проекта (миграции, статика, суперюзер) командой:
```
docker-compose exec web bash web-first-run.sh
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
Python Developer
