from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Document Generator"
    debug: bool = True


settings = Settings()
