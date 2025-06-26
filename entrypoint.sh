#!/bin/sh

# Выходим из скрипта, если любая команда завершится с ошибкой
set -e

# Ожидаем, пока база данных будет готова к приему соединений
# Мы используем nc (netcat), который нужно будет установить
until nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  echo "Waiting for database..."
  sleep 1
done
echo "Database started"

# Применяем миграции базы данных
python manage.py migrate

# Запускаем команду, которая была передана в docker-compose
# Например, `gunicorn core.wsgi:application --bind 0.0.0.0:8000`
exec "$@"