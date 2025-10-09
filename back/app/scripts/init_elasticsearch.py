#!/usr/bin/env python3
"""
Скрипт для инициализации индексов Elasticsearch.

Использование:
    docker-compose -p levelupper exec backend python scripts/init_elasticsearch.py
"""

import logging
import asyncio
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем корневую папку проекта в Python path
sys.path.insert(0, '/usr/src/app')

from src.elasticsearch.client import elasticsearch_client


async def main():
    """Главная функция для инициализации индексов"""
    logger.info("Запуск инициализации индексов Elasticsearch...")

    try:
        # Попытка подключения к Elasticsearch
        await elasticsearch_client.connect()
        logger.info("Подключение к Elasticsearch успешно!")

        # Создание всех индексов
        success = await elasticsearch_client.setup_indices()

        if success:
            logger.info("Все индексы Elasticsearch созданы успешно!")
        else:
            logger.error("Ошибка при создании индексов!")
            return 1

    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        return 1
    finally:
        # Закрытие соединения
        await elasticsearch_client.disconnect()

    return 0


if __name__ == "__main__":
    # Запуск асинхронного main
    exit_code = asyncio.run(main())
    sys.exit(exit_code)