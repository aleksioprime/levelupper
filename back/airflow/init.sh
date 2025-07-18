#!/bin/bash
set -e

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
