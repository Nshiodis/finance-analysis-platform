from pathlib import Path

import pytest
from pydantic import ValidationError

from finance_analysis.config import PROJECT_ROOT, Settings


@pytest.fixture
def clean_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """隔离：删掉 FINANCE_* 环境变量 + 切到空目录，让 Settings 读不到项目 .env"""
    for key in ("FINANCE_ENVIRONMENT", "FINANCE_LOG_LEVEL", "FINANCE_DATABASE_PATH"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.chdir(tmp_path)


def test_defaults(clean_env: None) -> None:
    """无任何覆盖时：默认 development / INFO / 默认库路径"""
    s = Settings()
    assert s.environment == "development"
    assert s.log_level == "INFO"
    assert s.database_path == PROJECT_ROOT / "database" / "finance.db"


def test_env_var_override(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """环境变量能覆盖默认值"""
    monkeypatch.setenv("FINANCE_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("FINANCE_DATABASE_PATH", str(PROJECT_ROOT / "tmp_test" / "x.db"))
    s = Settings()
    assert s.log_level == "ERROR"
    assert s.database_path == PROJECT_ROOT / "tmp_test" / "x.db"


def test_environment_must_be_valid(clean_env: None, monkeypatch: pytest.MonkeyPatch) -> None:
    """非法环境值启动即报错（fail fast）"""
    monkeypatch.setenv("FINANCE_ENVIRONMENT", "staging")
    with pytest.raises(ValidationError):
        Settings()


def test_prefix_protects_against_bare_env_var(
    clean_env: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """裸的 DATABASE_PATH 无法劫持配置（env_prefix 的意义）"""
    monkeypatch.setenv("DATABASE_PATH", "D:/evil/other.db")
    s = Settings()
    assert s.database_path == PROJECT_ROOT / "database" / "finance.db"