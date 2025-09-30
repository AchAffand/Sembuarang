from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	api_admin_key: str = Field(..., alias="API_ADMIN_KEY")
	database_url: str = Field("sqlite:///./data.db", alias="DATABASE_URL")
	twilio_lookup_sid: str | None = Field(None, alias="TWILIO_LOOKUP_SID")
	twilio_lookup_token: str | None = Field(None, alias="TWILIO_LOOKUP_TOKEN")
	app_env: str = Field("development", alias="APP_ENV")

	class Config:
		env_file = ".env"
		case_sensitive = False


settings = Settings()