"""
Инициализация Elasticsearch подключения.
"""

from src.common.elasticsearch.service import ElasticsearchService

# Глобальный экземпляр сервиса Elasticsearch
elasticsearch_service: ElasticsearchService = None


async def init_elasticsearch():
    """Инициализирует подключение к Elasticsearch."""
    global elasticsearch_service
    elasticsearch_service = ElasticsearchService()
    return elasticsearch_service


async def close_elasticsearch():
    """Закрывает подключение к Elasticsearch."""
    global elasticsearch_service
    if elasticsearch_service:
        await elasticsearch_service.close()


def get_elasticsearch_service() -> ElasticsearchService:
    """Возвращает экземпляр сервиса Elasticsearch."""
    global elasticsearch_service
    if not elasticsearch_service:
        raise RuntimeError("Elasticsearch service not initialized")
    return elasticsearch_service