#!/bin/bash

# 🚀 Инициализация БД
airflow db migrate

# 👤 Создание админа, если ещё не существует
airflow users create \
  --username "${AIRFLOW_ADMIN_USERNAME}" \
  --password "${AIRFLOW_ADMIN_PASSWORD}" \
  --firstname "${AIRFLOW_ADMIN_FIRSTNAME}" \
  --lastname "${AIRFLOW_ADMIN_LASTNAME}" \
  --role Admin \
  --email "${AIRFLOW_ADMIN_EMAIL}" || true

# 🚦 Запуск airflow (webserver или scheduler)
exec airflow "$@"
