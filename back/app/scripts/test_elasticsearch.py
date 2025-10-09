#!/usr/bin/env python3
"""
Скрипт для тестирования подключения к Elasticsearch и просмотра индексов.

Использование:
    docker-compose exec backend python scripts/test_elasticsearch.py
"""

import logging
import asyncio
import sys
from typing import Dict, List, Any

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, '/usr/src/app')

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, AuthorizationException

from src.core.config import settings

class ElasticsearchTester:
    """Класс для тестирования подключения к Elasticsearch"""

    def __init__(self):
        self.es_config = settings.elasticsearch
        self._client: AsyncElasticsearch = None

    async def create_client(self) -> AsyncElasticsearch:
        """Создание клиента Elasticsearch"""
        try:
            if self._client is not None:
                return self._client

            client_config = {
                "hosts": [self.es_config.url],
                "request_timeout": self.es_config.timeout,
                "retry_on_timeout": True,
            }

            if hasattr(self.es_config, 'use_ssl') and self.es_config.use_ssl:
                client_config["verify_certs"] = getattr(self.es_config, 'verify_certs', False)
                client_config["ssl_show_warn"] = False

            self._client = AsyncElasticsearch(**client_config)
            return self._client

        except Exception as e:
            logger.error(f"Ошибка создания клиента Elasticsearch: {e}")
            raise

    async def test_connection(self) -> bool:
        """Тестирование подключения к Elasticsearch"""
        logger.info("🔍 Тестирование подключения к Elasticsearch...")
        logger.info(f"📡 URL: {self.es_config.url}")

        try:
            client = await self.create_client()

            # Проверка ping
            if await client.ping():
                logger.info("Подключение к Elasticsearch успешно!")
                return True
            else:
                logger.info("Не удалось подключиться к Elasticsearch (ping failed)")
                return False

        except ConnectionError as e:
            logger.error(f"Ошибка подключения к Elasticsearch: {e}")
            return False
        except AuthorizationException as e:
            logger.error(f"Ошибка авторизации в Elasticsearch: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при подключении к Elasticsearch: {e}")
            return False

    async def get_cluster_health(self) -> Dict[str, Any]:
        """Получение информации о здоровье кластера"""
        logger.info("Проверка здоровья кластера...")

        try:
            client = await self.create_client()
            health = await client.cluster.health()

            status_emoji = {
                'green': '🟢',
                'yellow': '🟡',
                'red': '🔴'
            }

            status = health.get('status', 'unknown')
            emoji = status_emoji.get(status, '⚪')

            logger.info(f"{emoji} Статус кластера: {status}")
            logger.info(f"Количество узлов: {health.get('number_of_nodes', 'N/A')}")
            logger.info(f"Узлы с данными: {health.get('number_of_data_nodes', 'N/A')}")
            logger.info(f"Активные шарды: {health.get('active_shards', 'N/A')}")

            if health.get('unassigned_shards', 0) > 0:
                logger.warning(f"Неназначенные шарды: {health['unassigned_shards']}")

            return health

        except Exception as e:
            logger.error(f"Ошибка получения информации о здоровье кластера: {e}")
            return {}

    async def get_cluster_stats(self) -> Dict[str, Any]:
        """Получение дополнительной статистики кластера"""
        try:
            client = await self.create_client()
            stats = await client.cluster.stats()

            logger.info(f"Общее количество индексов: {stats.get('indices', {}).get('count', 'N/A')}")
            logger.info(f"Общее количество документов: {stats.get('indices', {}).get('docs', {}).get('count', 'N/A')}")
            logger.info(f"Общий размер данных: {stats.get('indices', {}).get('store', {}).get('size', 'N/A')}")

            return stats

        except Exception as e:
            logger.error(f"Ошибка получения статистики кластера: {e}")
            return {}

    async def list_indices(self) -> List[Dict[str, Any]]:
        """Получение списка всех индексов"""
        logger.info("Получение списка индексов...")

        try:
            client = await self.create_client()

            # Получаем информацию об индексах в JSON формате
            indices = await client.cat.indices(format='json', s='index')

            if not indices:
                logger.info("📭 Индексы не найдены")
                return []

            # Фильтруем системные индексы (начинающиеся с точки)
            user_indices = [idx for idx in indices if not idx['index'].startswith('.')]
            system_indices = [idx for idx in indices if idx['index'].startswith('.')]

            logger.info(f"Найдено индексов:")
            logger.info(f"Пользовательские: {len(user_indices)}")
            logger.info(f"Системные: {len(system_indices)}")

            if user_indices:
                logger.info("Пользовательские индексы:")
                for idx in user_indices:
                    health_emoji = {'green': '🟢', 'yellow': '🟡', 'red': '🔴'}.get(idx.get('health', ''), '⚪')
                    logger.info(f"{health_emoji} {idx['index']}")
                    logger.info(f"Документов: {idx.get('docs.count', 'N/A')}")
                    logger.info(f"Размер: {idx.get('store.size', 'N/A')}")
                    logger.info(f"Статус: {idx.get('status', 'N/A')}")

            if system_indices and len(system_indices) <= 10:  # Показываем только первые 10 системных
                logger.info(f"Системные индексы (первые {min(10, len(system_indices))}):")
                for idx in system_indices[:10]:
                    logger.info(f"• {idx['index']}")
            elif system_indices:
                logger.info(f"Системные индексы: {len(system_indices)} (скрыты)")

            return indices

        except Exception as e:
            logger.error(f"Ошибка получения списка индексов: {e}")
            return []

    async def test_index_operations(self):
        """Тестирование базовых операций с индексом"""
        test_index = "test_connection_index"
        logger.info(f"Тестирование операций с индексом '{test_index}'...")

        try:
            client = await self.create_client()

            # Создаем тестовый документ
            test_doc = {
                "title": "Test Document",
                "content": "This is a test document for connection testing",
                "timestamp": "2024-01-01T00:00:00Z"
            }

            # Индексируем документ с принудительным обновлением
            response = await client.index(
                index=test_index,
                id="test_doc_1",
                document=test_doc,
                refresh="wait_for"  # Ждем обновления индекса
            )
            logger.info(f"✅ Документ создан: {response['result']}")

            # Получаем документ по ID
            doc = await client.get(index=test_index, id="test_doc_1")
            logger.info(f"✅ Документ получен по ID: {doc['_source']['title']}")

            # Поиск документа (теперь должен найти)
            search_response = await client.search(
                index=test_index,
                query={"match": {"title": "Test"}}
            )
            hits = search_response['hits']['total']['value']
            logger.info(f"✅ Найдено документов при поиске: {hits}")

            # Покажем детали найденных документов
            if hits > 0:
                for hit in search_response['hits']['hits']:
                    logger.info(f"   📄 Найден: {hit['_source']['title']} (score: {hit['_score']})")
            else:
                logger.warning("⚠️  Документы не найдены при поиске!")

            # Дополнительные тесты поиска
            logger.info("🔍 Тестирование различных типов поиска...")

            # Поиск всех документов
            all_docs = await client.search(index=test_index, query={"match_all": {}})
            logger.info(f"📊 Всего документов в индексе: {all_docs['hits']['total']['value']}")

            # Поиск по содержимому
            content_search = await client.search(
                index=test_index,
                query={"match": {"content": "test"}}
            )
            logger.info(f"🔍 Найдено по содержимому 'test': {content_search['hits']['total']['value']}")

            # Wildcard поиск
            wildcard_search = await client.search(
                index=test_index,
                query={"wildcard": {"title": "*Test*"}}
            )
            logger.info(f"🎯 Найдено wildcard поиском '*Test*': {wildcard_search['hits']['total']['value']}")

            # Удаляем тестовый индекс
            await client.indices.delete(index=test_index)
            logger.info(f"Тестовый индекс '{test_index}' удален")

            return True

        except Exception as e:
            logger.error(f"Ошибка при тестировании операций с индексом: {e}")
            # Пытаемся удалить тестовый индекс в случае ошибки
            try:
                await client.indices.delete(index=test_index, ignore=[404])
            except:
                pass
            return False

    async def run_full_test(self):
        """Запуск полного теста Elasticsearch"""
        logger.info("Запуск полного теста Elasticsearch")

        # Тест подключения
        connection_ok = await self.test_connection()
        if not connection_ok:
            logger.error("Тестирование прервано из-за ошибки подключения")
            return

        # Информация о кластере
        await self.get_cluster_health()

        # Дополнительная статистика
        await self.get_cluster_stats()

        # Список всех индексов
        await self.list_indices()

        # Тестирование операций с данными
        await self.test_index_operations()

        logger.info("✅ Тестирование Elasticsearch завершено успешно!")

    async def close(self):
        """Закрытие соединения"""
        if self._client:
            await self._client.close()


async def main():
    """Главная функция"""
    tester = ElasticsearchTester()

    try:
        await tester.run_full_test()
    except Exception as e:
        logger.error(f"Тестирование прервано: {e}")
    finally:
        await tester.close()


if __name__ == "__main__":
    # Запуск асинхронного main
    asyncio.run(main())