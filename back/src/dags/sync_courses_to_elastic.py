from datetime import datetime

from airflow import DAG
from airflow.operators.python import AsyncPythonOperator
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis

from courses.infrastructure.etl.elastic import CourseElasticSyncService
from courses.infrastructure.etl.manager import RedisSyncStateManager
from common.db.postgres import async_session_maker


default_args = {
    "start_date": datetime(2024, 1, 1),
}

with DAG(
    dag_id="sync_courses_to_elastic",
    schedule_interval="*/15 * * * *",  # ⏰ каждые 15 минут
    default_args=default_args,
    catchup=False,
    tags=["etl", "elasticsearch"],
) as dag:

    async def sync_to_elastic():
        # ✅ Инициализация клиентов
        redis_client = redis.Redis(host="redis", port=6379, decode_responses=True)
        es = AsyncElasticsearch(hosts=["http://elasticsearch:9200"])
        redis_key = "sync:courses_full:last_updated_at"
        state_manager = RedisSyncStateManager(redis_client, redis_key)

        # ✅ Получаем время последней синхронизации
        last_sync_time = await state_manager.get_last_sync_time()

        async with async_session_maker() as session:
            sync_service = CourseElasticSyncService(es, session)
            now = await sync_service.sync(last_sync_time)

        # ✅ Сохраняем время последней синхронизации
        await state_manager.set_last_sync_time(now)

    # 🔁 Асинхронный Python-оператор
    run_sync = AsyncPythonOperator(
        task_id="run_full_sync",
        python_callable=sync_to_elastic,
    )
