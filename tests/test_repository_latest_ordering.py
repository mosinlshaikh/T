from trading_os.db.repository import TradingOSRepository


def test_limited_decisions_return_latest_rows_in_chronological_order(tmp_path):
    repository = TradingOSRepository.from_database_url(
        f"sqlite:///{tmp_path / 'ordering.sqlite3'}"
    )

    for index in range(5):
        repository.save_ai_decision(
            {
                "action": "SKIP",
                "timestamp": f"2026-07-21T00:0{index}:00+00:00",
                "index": index,
            }
        )
        repository.save_audit_event(
            {
                "event_type": "paper_auto_trader_tick",
                "created_at": f"2026-07-21T00:0{index}:00+00:00",
                "payload": {"index": index},
            }
        )

    assert [item["index"] for item in repository.list_ai_decisions(2)] == [3, 4]
    assert [item["payload"]["index"] for item in repository.list_audit_events(2)] == [3, 4]
