from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 8001
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "wantedlab"
    DB_ECHO: bool = True

    model_config = {
        "case_sensitive": True,
        "env_file": ".env.dev"
    }


# 설정 인스턴스 생성
settings = Settings()

# 명시적으로 export
__all__ = ["settings", "Settings"]