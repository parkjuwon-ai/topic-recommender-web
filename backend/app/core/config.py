from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bookend Topic Recommender API"
    environment: str = "local"

    # DB
    database_url: str = (
        "postgresql+psycopg2://parkseoul@localhost:5432/bookend_topics"
    )

    # ✅ JWT 설정
    jwt_secret_key: str = "change-me-in-.env"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ✅ 구글 로그인용 클라이언트 ID (나중에 콘솔에서 받아서 .env에 넣을 값)
    google_client_id: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
    )


settings = Settings()

