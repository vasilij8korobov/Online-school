# Инструкция по запуску проекта
## Требования
* Установленный Docker и Docker Compose
* Файл .env с переменными окружения (создать на основе .env.example)

## Запуск проекта
1. Создайте файл .env в корне проекта и заполните его по шаблону .env.example
2. Соберите и запустите контейнеры:
    docker-compose up -d --build
3. Примените миграции (если Django не делает это автоматически):
    docker-compose exec web python manage.py migrate
4. Создайте суперпользователя (опционально):
    docker-compose exec web python manage.py createsuperuser

## Сервисы и их порты
Сервис	        Порт	    Доступ
Django	        8000	    http://localhost:8000
PostgreSQL	    5432	    db:5432 (внутри сети)
Redis	        6379	    redis:6379 (внутри сети)

## Проверка работоспособности
* Django: Откройте в браузере http://localhost:8000
* PostgreSQL: Проверьте логи:
    docker-compose logs db
* Redis: Проверьте подключение:
    docker-compose exec redis redis-cli ping
* Celery (Worker): Проверьте логи:
    docker-compose logs celery
* Celery Beat: Проверьте логи:
    docker-compose logs celery-beat

## Остановка проекта
* Остановить контейнеры (без удаления данных):
    docker-compose down
* Полная очистка (включая базу данных и volumes):
    docker-compose down -v

## Дополнительные команды
* Просмотр логов:
    docker-compose logs -f [service_name]
* Запуск тестов:
    docker-compose exec web python manage.py test

## Развертывание на сервере (CI/CD)
1. При пуше в ветку `main` или `develop` автоматически запускается:
   - Тестирование (`flake8`, `pytest`).
   - Сборка Docker-образа.
   - Деплой на сервер через SSH.
2. Требуемые secrets в GitHub:
   - `DOCKERHUB_USERNAME` — логин Docker Hub.
   - `DOCKERHUB_TOKEN` — токен Docker Hub.
   - `SSH_KEY` — приватный ключ для доступа к серверу.
   - `SSH_USER` — пользователь сервера (например, `vasiliy`).
   - `SERVER_IP` — IP сервера (51.250.99.83).
