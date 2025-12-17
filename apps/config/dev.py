from typing import Final, Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

from .base import ENV_PATH

load_dotenv(ENV_PATH)


class PostgresSettings(BaseSettings):
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    host: str = "localhost"
    port: int = 5432
    db: str = "postgres"
    driver: Literal["asyncpg"] = "asyncpg"

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    @property
    def sqlalchemy_url(self) -> str:
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class MinioSettings(BaseSettings):
    url: str = "<URL>"
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    bucket: str = "dev"

    model_config = SettingsConfigDict(env_prefix="MINIO_")


class RabbitMQSettings(BaseSettings):
    user: str = "<USER>"
    password: str = "<PASSWORD>"
    host: str = "localhost"
    port: int = 5672

    model_config = SettingsConfigDict(env_prefix="RABBITMQ_")

    @property
    def url(self) -> str:
        return ...


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/0"


class SaluteSpeechSettings(BaseSettings):
    apikey: str = "<APIKEY>"
    scope: str = "<SCOPE>"
    client_id: str = "<CLIENT_ID>"
    client_secret: str = "<CLIENT_SECRET>"

    model_config = SettingsConfigDict(env_prefix="SALUTE_SPEECH")


class JWTSettings(BaseSettings):
    secret_key: str = "<SECRET_KEY>"
    algorithm: str = "HS256"
    user_access_token_expires_in_minutes: int = 15
    user_refresh_token_expires_in_days: int = 7
    guest_access_token_expires_in_days: int = 10

    model_config = SettingsConfigDict(env_prefix="JWT_")


class EncryptionSettings(BaseSettings):
    key: str = "<KEY>"
    salt: str = "<SALT>"
    iterations: int = 100_000
    key_length: int = 32

    model_config = SettingsConfigDict(env_prefix="ENCRYPTION_")


class VKSettings(BaseSettings):
    client_id: str = "<CLIENT_ID>"
    client_secret: str = "<CLIENT_SECRET>"
    base_url: str = "https://id.vk.ru"
    redirect_uri: str = "http://localhost:8000/api/v1/auth/vk/callback"

    model_config = SettingsConfigDict(env_prefix="VK_")


class OAuthSettings(BaseSettings):
    pkce_session_expires_in_minutes: int = 10

    model_config = SettingsConfigDict(env_prefix="OAUTH_")


class EmbeddingsSettings(BaseSettings):
    base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(env_prefix="EMBEDDINGS_")


class MailRuSettings(BaseSettings):
    password: str = "<PASSWORD>"

    model_config = SettingsConfigDict(env_prefix="MAILRU_")


class AppSettings(BaseSettings):
    name: str = "Alyosha AI"
    port: int = 8000
    host: str = "localhost"
    title: str = "<TITLE>"
    version: str = "0.1.0"

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    postgres: PostgresSettings = PostgresSettings()
    minio: MinioSettings = MinioSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    redis: RedisSettings = RedisSettings()
    salute_speech: SaluteSpeechSettings = SaluteSpeechSettings()
    jwt: JWTSettings = JWTSettings()
    vk: VKSettings = VKSettings()
    oauth: OAuthSettings = OAuthSettings()
    embeddings: EmbeddingsSettings = EmbeddingsSettings()
    mailru: MailRuSettings = MailRuSettings()
    encryption: EncryptionSettings = EncryptionSettings()


settings: Final[Settings] = Settings()
