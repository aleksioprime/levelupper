"""Клиент для подключения к Elasticsearch"""

import json
import os
import logging
from typing import Optional

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, NotFoundError

from src.core.config import settings

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Клиент для работы с Elasticsearch"""

    def __init__(self):
        self._client: Optional[AsyncElasticsearch] = None
        self._es_config = settings.elasticsearch

    async def get_client(self) -> AsyncElasticsearch:
        """Получить клиент Elasticsearch"""
        if self._client is None:
            await self.connect()
        return self._client

    async def connect(self) -> None:
        """Подключиться к Elasticsearch"""
        try:
            client_config = {
                "hosts": [self._es_config.url],
                "timeout": self._es_config.timeout,
                "max_retries": self._es_config.max_retries,
                "retry_on_timeout": True,
            }

            if self._es_config.use_ssl:
                client_config["verify_certs"] = self._es_config.verify_certs
                client_config["ssl_show_warn"] = False

            self._client = AsyncElasticsearch(**client_config)

            # Проверка подключения
            await self._client.ping()
            logger.info("Successfully connected to Elasticsearch")

        except ConnectionError as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Elasticsearch: {e}")
            raise

    async def disconnect(self) -> None:
        """Отключиться от Elasticsearch"""
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Elasticsearch")

    async def create_index(self, index_name: str, mapping_file: str) -> bool:
        """Создать индекс с маппингом из файла"""
        try:
            client = await self.get_client()

            # Проверить, существует ли индекс
            if await client.indices.exists(index=index_name):
                logger.info(f"Index {index_name} already exists")
                return True

            # Загрузить маппинг из файла
            mapping_path = os.path.join(
                os.path.dirname(__file__),
                "indices",
                mapping_file
            )

            if not os.path.exists(mapping_path):
                logger.error(f"Mapping file not found: {mapping_path}")
                return False

            with open(mapping_path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)

            # Создать индекс
            await client.indices.create(
                index=index_name,
                body=mapping
            )

            logger.info(f"Successfully created index {index_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            return False

    async def delete_index(self, index_name: str) -> bool:
        """Удалить индекс"""
        try:
            client = await self.get_client()
            await client.indices.delete(index=index_name)
            logger.info(f"Successfully deleted index {index_name}")
            return True
        except NotFoundError:
            logger.warning(f"Index {index_name} not found")
            return True
        except Exception as e:
            logger.error(f"Failed to delete index {index_name}: {e}")
            return False

    async def index_exists(self, index_name: str) -> bool:
        """Проверить существование индекса"""
        try:
            client = await self.get_client()
            return await client.indices.exists(index=index_name)
        except Exception as e:
            logger.error(f"Failed to check index existence {index_name}: {e}")
            return False

    async def setup_indices(self) -> bool:
        """Создать все необходимые индексы"""
        indices = [
            (self._es_config.courses_index, "courses_index.json"),
            (self._es_config.course_topics_index, "course_topics_index.json"),
            (self._es_config.lessons_index, "lessons_index.json"),
        ]

        success = True
        for index_name, mapping_file in indices:
            if not await self.create_index(index_name, mapping_file):
                success = False

        return success


# Глобальный экземпляр клиента
elasticsearch_client = ElasticsearchClient()


async def get_elasticsearch_client() -> AsyncElasticsearch:
    """Dependency для получения клиента Elasticsearch"""
    return await elasticsearch_client.get_client()


__all__ = ["ElasticsearchClient", "elasticsearch_client", "get_elasticsearch_client"]