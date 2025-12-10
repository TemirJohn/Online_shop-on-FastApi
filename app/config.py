from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "My Shop API"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    
    postgres_user: str = "temirzhan"
    postgres_password: str = "11466795"
    postgres_db: str = "shop_db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    class Config:
        env_file = ".env"


settings = Settings()