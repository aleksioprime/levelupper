from pydantic import Field
from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    """
    Конфигурация для настроек базы данных
    """
    name: str = Field(alias='DB_NAME', default='database')
    user: str = Field(alias='DB_USER', default='admin')
    password: str = Field(alias='DB_PASSWORD', default='123qwe')
    host: str = Field(alias='DB_HOST', default='127.0.0.1')
    port: int = Field(alias='DB_PORT', default=5432)
    show_query: bool = Field(alias='SHOW_SQL_QUERY', default=False)

    @property
    def _base_url(self) -> str:
        """ Формирует базовый URL для подключения к базе данных """
        return f"{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @property
    def dsn(self) -> str:
        """ Формирует DSN строку для подключения к базе данных с использованием asyncpg """
        return f"postgresql+asyncpg://{self._base_url}"


class AuthServiceSettings(BaseSettings):
    """
    Конфигурация для взаимодействия с auth-сервисом
    """
    url: str = Field(alias='AUTH_SERVICE_URL', default='http://levelupper-auth-app:8000')
    timeout: float = Field(alias='AUTH_SERVICE_TIMEOUT', default=30.0)
    max_batch_size: int = Field(alias='AUTH_SERVICE_MAX_BATCH_SIZE', default=100)
    service_token: str = Field(alias='AUTH_SERVICE_TOKEN', default='')


class ElasticsearchSettings(BaseSettings):
    """
    Конфигурация для подключения к Elasticsearch
    """
    host: str = Field(alias='ELASTICSEARCH_HOST', default='127.0.0.1')
    port: int = Field(alias='ELASTICSEARCH_PORT', default=9200)
    username: str = Field(alias='ELASTICSEARCH_USERNAME', default='')
    password: str = Field(alias='ELASTICSEARCH_PASSWORD', default='')
    use_ssl: bool = Field(alias='ELASTICSEARCH_USE_SSL', default=False)
    verify_certs: bool = Field(alias='ELASTICSEARCH_VERIFY_CERTS', default=False)
    timeout: float = Field(alias='ELASTICSEARCH_TIMEOUT', default=30.0)
    max_retries: int = Field(alias='ELASTICSEARCH_MAX_RETRIES', default=3)

    # Индексы
    courses_index: str = Field(alias='ELASTICSEARCH_COURSES_INDEX', default='courses')
    course_topics_index: str = Field(alias='ELASTICSEARCH_COURSE_TOPICS_INDEX', default='course_topics')
    lessons_index: str = Field(alias='ELASTICSEARCH_LESSONS_INDEX', default='lessons')

    @property
    def url(self) -> str:
        """Формирует URL для подключения к Elasticsearch"""
        protocol = 'https' if self.use_ssl else 'http'
        if self.username and self.password:
            return f"{protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{protocol}://{self.host}:{self.port}"


class Settings(BaseSettings):

    db: DBSettings = DBSettings()
    auth_service: AuthServiceSettings = AuthServiceSettings()
    elasticsearch: ElasticsearchSettings = ElasticsearchSettings()


settings = Settings()
