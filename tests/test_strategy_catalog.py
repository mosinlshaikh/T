from trading_os.strategies.catalog import strategy_catalog_payload


def test_strategy_catalog_is_paper_only_and_complete() -> None:
    payload = strategy_catalog_payload()

    assert payload["live_execution_available"] is False
    assert payload["withdrawals_supported"] is False
    assert payload["external_ai_key_required"] is False
    assert payload["strategy_count"] >= 15
    assert "No Data = No Trade" in payload["master_rules"]


def test_strategy_catalog_items_require_evidence() -> None:
    payload = strategy_catalog_payload()

    for strategy in payload["strategies"]:
        assert strategy["status"] == "PAPER_ADVISORY"
        assert strategy["required_data"]
        assert "Evidence required" in strategy["safety_rules"]
