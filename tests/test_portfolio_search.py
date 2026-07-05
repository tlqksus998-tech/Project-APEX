from app.ui.portfolio_view import build_search_results

SAMSUNG = "\uc0bc\uc131"
SK_HYNIX = "SK\ud558\uc774\ub2c9\uc2a4"
TIGER_SP500 = "TIGER \ubbf8\uad6dS&P500"
MICRON_KO = "\ub9c8\uc774\ud06c\ub860"


def labels(query: str) -> list[str]:
    return [result.label for result in build_search_results(query)]


def test_search_suggests_samsung_names():
    result_labels = labels(SAMSUNG)

    assert "\uc0bc\uc131\uc804\uc790 (005930)" in result_labels
    assert "\uc0bc\uc131SDI (006400)" in result_labels


def test_search_resolves_requested_inputs():
    assert build_search_results(SK_HYNIX)[0].ticker == "000660"
    assert build_search_results(TIGER_SP500)[0].ticker == "360750"
    assert build_search_results("KORU")[0].ticker == "KORU"
    assert build_search_results("MU")[0].ticker == "MU"
    assert build_search_results(MICRON_KO)[0].ticker == "MU"
