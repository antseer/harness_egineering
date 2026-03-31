from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Task Manager API"
    database_url: str = "sqlite:///./tasks.db"
    debug: bool = False

    # JWT 配置
    secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    model_config = {"env_prefix": "TASK_"}


settings = Settings()
