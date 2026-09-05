from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录是"文件系统事实"，不是可配置项，保持模块级常量
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """集中配置：默认值写在代码里，可由 .env / 环境变量覆盖"""

    environment: Literal["development", "testing", "production"] = "development"

    data_path: Path = PROJECT_ROOT / "data"
    output_path: Path = PROJECT_ROOT / "output"
    database_path: Path = PROJECT_ROOT / "database" / "finance.db"
    log_path: Path = PROJECT_ROOT / "output" / "logs" / "finance.log"
    log_level: str = "INFO"     # DEBUG < INFO < WARNING < ERROR

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="FINANCE_",
        extra="ignore",
    )


settings = Settings()