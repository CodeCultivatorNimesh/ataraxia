from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App
    app_name: str = "trading-middleware"
    app_env: str = "development"
    app_port: int = 8000
    secret_key: str = "change-this-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://trading_user:password@localhost:5432/trading_middleware"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "trading_middleware"
    postgres_user: str = "trading_user"
    postgres_password: str = "password"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Alpaca
    alpaca_api_key: str = ""
    alpaca_secret_key: str = ""
    alpaca_base_url: str = "https://paper-api.alpaca.markets"
    alpaca_data_url: str = "https://data.alpaca.markets"

    # Binance
    binance_api_key: str = ""
    binance_secret_key: str = ""
    binance_testnet: bool = True

    # Risk defaults
    max_daily_loss_pct: float = 5.0
    max_risk_per_trade_pct: float = 2.0
    max_open_trades: int = 5
    max_crypto_positions_isolated: int = 3

    # Pattern alerts
    pattern_alert_enabled: bool = True
    pattern_min_confidence: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

settings = Settings()
