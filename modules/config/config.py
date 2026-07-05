import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Application settings loaded from defaults and environment variables."""

    project_name: str
    project_subtitle: str
    version: str
    sprint_name: str
    environment: str
    base_dir: Path
    dummy_price: float
    concentration_limit: float
    cash_minimum_weight: float
    market_default_period: str
    market_default_interval: str
    market_dummy_days: int


def get_config() -> AppConfig:
    """Return the Project APEX runtime configuration."""

    base_dir = Path(__file__).resolve().parents[2]
    return AppConfig(
        project_name=os.getenv("APEX_PROJECT_NAME", "Project APEX"),
        project_subtitle=os.getenv("APEX_PROJECT_SUBTITLE", "AI Portfolio Expert"),
        version=os.getenv("APEX_VERSION", "0.2.1"),
        sprint_name=os.getenv("APEX_SPRINT", "Epic 2 - Sprint 2.1 Market Engine"),
        environment=os.getenv("APEX_ENV", "local"),
        base_dir=base_dir,
        dummy_price=float(os.getenv("APEX_DUMMY_PRICE", "100.0")),
        concentration_limit=float(os.getenv("APEX_CONCENTRATION_LIMIT", "0.40")),
        cash_minimum_weight=float(os.getenv("APEX_CASH_MINIMUM_WEIGHT", "0.10")),
        market_default_period=os.getenv("APEX_MARKET_DEFAULT_PERIOD", "6mo"),
        market_default_interval=os.getenv("APEX_MARKET_DEFAULT_INTERVAL", "1d"),
        market_dummy_days=int(os.getenv("APEX_MARKET_DUMMY_DAYS", "30")),
    )
