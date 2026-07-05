import pandas as pd

from modules.portfolio.storage import delete_saved_portfolio, load_portfolio_json, save_portfolio_json


def test_save_and_load_portfolio_json(tmp_path):
    path = tmp_path / "portfolio.json"
    portfolio = pd.DataFrame(
        [
            {"name": "Apple", "ticker": "AAPL", "quantity": 2, "avg_price": 100},
            {"name": "\uc0bc\uc131\uc804\uc790", "ticker": "005930", "quantity": 1, "avg_price": 70000},
        ]
    )

    success, message = save_portfolio_json(portfolio, path)
    loaded, error = load_portfolio_json(path)

    assert success, message
    assert error is None
    assert loaded["ticker"].tolist() == ["AAPL", "005930"]
    assert loaded["quantity"].tolist() == [2, 1]


def test_load_missing_portfolio_is_safe(tmp_path):
    loaded, error = load_portfolio_json(tmp_path / "missing.json")

    assert loaded.empty
    assert error is not None


def test_delete_saved_portfolio_is_safe(tmp_path):
    path = tmp_path / "portfolio.json"
    save_portfolio_json(pd.DataFrame([{"name": "A", "ticker": "AAPL", "quantity": 1, "avg_price": 1}]), path)

    success, message = delete_saved_portfolio(path)

    assert success, message
    assert not path.exists()
