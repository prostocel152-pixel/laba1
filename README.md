# Django Labs

Учебный Django-проект для управления проектами и задачами. Включает модели
проектов, участников и задач, REST API с JWT-аутентификацией, фильтрацию,
статистику проектов и документацию Swagger.

## Требования

- Python 3.12
- PostgreSQL

## Установка и запуск (Windows PowerShell)

Из корневой папки проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Создайте `.env` в корне проекта со своими локальными параметрами подключения:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-local-secret-key
DB_NAME=django_labs
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
```

Создайте базу данных `django_labs` в PostgreSQL, если она ещё не существует.
Значения `DB_NAME`, `DB_USER` и `DB_PASSWORD` в `.env` должны соответствовать
настройкам вашего PostgreSQL. Не публикуйте `.env` и не используйте приведённый
примерный ключ как production-секрет.

Примените миграции, создайте учётную запись администратора и запустите сервер:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Django Admin: <http://127.0.0.1:8000/admin/>
- Swagger UI: <http://127.0.0.1:8000/api/docs/>
- OpenAPI-схема: <http://127.0.0.1:8000/api/schema/>

## API

Основные маршруты:

- `GET/POST /api/projects/` — список и создание доступных проектов
- `GET /api/projects/{id}/stats/` — статистика задач проекта
- `POST /api/projects/{id}/members/` — добавление участника администратором
- `GET/POST /api/tasks/` — список и создание задач
- `GET /api/token/` — получение JWT access/refresh токенов
- `POST /api/token/refresh/` — обновление access-токена

Для защищённых API-запросов передавайте access-токен в заголовке:

```text
Authorization: Bearer <access-token>
```

Для фильтрации задач доступны параметры `status`, `project` и `assigned_to`,
например: `/api/tasks/?status=TODO&project=1`.

## Тесты и демоданные

Запуск тестов:

```powershell
python manage.py test
```

В корне также находятся учебные скрипты `seed_demo.py`, `seed_large.py` и
`report_orm.py`. Первый создаёт демонстрационных пользователей, проекты и задачи;
второй создаёт большой набор данных для ORM-упражнений (после запуска `seed_demo.py`).
Их можно выполнить через Django shell из PowerShell:

```powershell
Get-Content .\seed_demo.py | python manage.py shell
Get-Content .\seed_large.py | python manage.py shell
Get-Content .\report_orm.py | python manage.py shell
```
