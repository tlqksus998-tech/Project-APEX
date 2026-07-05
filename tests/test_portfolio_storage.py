import pandas as pd

from modules.portfolio.storage import delete_saved_portfolio, load_portfolio_json, load_portfolio_json_bytes, portfolio_to_json_bytes, save_portfolio_json, validate_portfolio_payload


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



def test_portfolio_to_json_bytes_blocks_empty_download():
    content, error = portfolio_to_json_bytes(pd.DataFrame())

    assert content is None
    assert error is not None


def test_portfolio_json_bytes_round_trip():
    portfolio = pd.DataFrame([{"name": "Apple", "ticker": "AAPL", "quantity": 2, "avg_price": 100}])
    content, error = portfolio_to_json_bytes(portfolio)
    loaded, load_error = load_portfolio_json_bytes(content or b"")

    assert error is None
    assert load_error is None
    assert loaded.iloc[0]["ticker"] == "AAPL"


def test_invalid_upload_schema_returns_friendly_error():
    loaded, error = validate_portfolio_payload({"schema_version": 1, "holdings": [{"ticker": "AAPL"}]})

    assert loaded.empty
    assert error == "\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ud30c\uc77c \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4."


def test_invalid_json_bytes_returns_friendly_error():
    loaded, error = load_portfolio_json_bytes(b"not-json")

    assert loaded.empty
    assert error == "\ud3ec\ud2b8\ud3f4\ub9ac\uc624 \ud30c\uc77c \ud615\uc2dd\uc774 \uc62c\ubc14\ub974\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4."
