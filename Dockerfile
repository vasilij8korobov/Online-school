# Указываем базовый образ
# FROM python:3.12



# Используем официальный образ Nginx
FROM nginx:latest

# Копируем файл конфигурации Nginx в контейнер
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем статические файлы веб-сайта в директорию для обслуживания
COPY html/ /usr/share/nginx/html

# Открываем порт 80 для HTTP-трафика
EXPOSE 80



# # Устанавливаем рабочую директорию в контейнере
# WORKDIR /app
#
# # Устанавливаем зависимости системы
# RUN apt-get update \
#     && apt-get install -y gcc libpq-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*
#
# # Копируем файл с зависимостями и устанавливаем их  " --no-cache-dir указывает pip не сохранять кэш"
# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
#
# # Копируем остальные файлы проекта в контейнер
# COPY . .
#
# # Создаем директорию длч хранения медиа файлов
# RUN mkdir -p /app/media
#
# # Открываем порт 8000 для взаимодействия с приложением
# EXPOSE 8000
#
# # Определяем команду для запуска приложения
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]