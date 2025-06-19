from pydantic import BaseSettings


class Settings(BaseSettings):
    # Database
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_ECHO: bool = True    

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()




