#!/bin/bash
set -e

# Установка дополнительных пакетов
if [ -f /requirements.txt ]; then
  echo "Установка дополнительных зависимостей..."
  pip install -r /requirements.txt
fi

# Инициализация БД (создаёт таблицы, если их нет)
airflow db migrate

# Создание админа, если ещё не существует
if ! airflow users list | grep -qw "${AIRFLOW_ADMIN_USERNAME}"; then
  airflow users create \
    --username "${AIRFLOW_ADMIN_USERNAME}" \
    --password "${AIRFLOW_ADMIN_PASSWORD}" \
    --firstname "${AIRFLOW_ADMIN_FIRSTNAME}" \
    --lastname "${AIRFLOW_ADMIN_LASTNAME}" \
    --role Admin \
    --email "${AIRFLOW_ADMIN_EMAIL}"
fi

# Запуск airflow (webserver или scheduler)
exec airflow "$@"
