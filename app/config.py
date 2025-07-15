# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # ArangoDB
    arango_url: str = Field("http://localhost:8529", env="ARANGO_URL")
    arango_user: str = Field("root", env="ARANGO_USER")
    arango_password: str = Field("admin", env="ARANGO_PASSWORD")
    arango_db: str = Field("follow_db", env="ARANGO_DB")
    test_arango_db: str = Field("test_follow_db", env="ARANGO_DB")

    # RabbitMQ
    rabbitmq_url: str = Field("amqp://guest:guest@localhost/", env="RABBITMQ_URL")
    rabbitmq_exchange: str = Field("user.events", env="RABBITMQ_EXCHANGE")
    queue_name: str = Field("user_created_queue", env="QUEUE_NAME")

    class Config:
        env_file = ".env"


settings = Settings()
