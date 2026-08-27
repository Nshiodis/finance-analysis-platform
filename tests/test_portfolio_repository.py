from pathlib import Path

import pytest

from finance_analysis.repository.portfolio_repository import PortfolioRepository


@pytest.fixture
def repo(tmp_path: Path) -> PortfolioRepository:
    """每个测试一个独立临时数据库"""
    return PortfolioRepository(tmp_path / "test.db")


def test_create_and_get(repo: PortfolioRepository) -> None:
    """创建后能查到，weights 原样返回（JSON 往返）"""
    pid = repo.create_portfolio({"600519": 0.5, "000858": 0.5})
    record = repo.get_portfolio(pid)
    assert record is not None            # 这行顺便做类型收窄
    assert record["id"] == pid
    assert record["weights"] == {"600519": 0.5, "000858": 0.5}


def test_get_missing(repo: PortfolioRepository) -> None:
    """不存在的 id → None（仓库语义）"""
    assert repo.get_portfolio(999) is None


def test_ids_increment(repo: PortfolioRepository) -> None:
    """自增 id：第二次创建 = 第一次 + 1"""
    pid1 = repo.create_portfolio({"600519": 1.0})
    pid2 = repo.create_portfolio({"000858": 1.0})
    assert pid2 == pid1 + 1


def test_json_roundtrip(repo: PortfolioRepository) -> None:
    """三个股票的权重 dict 往返无损"""
    weights = {"600519": 0.3, "000858": 0.3, "300750": 0.4}
    pid = repo.create_portfolio(weights)
    record = repo.get_portfolio(pid)   # 第一步：先取出来
    assert record is not None          # 第二步：先收窄（顺便就是运行时断言）
    assert record["weights"] == weights  # 第三步：再安全使用