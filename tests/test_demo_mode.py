from modes.demo_mode import run_demo

def test_demo_mode_generates_signal():
    signals = run_demo("data/sample/btc_demo.csv", send_telegram=False)
    assert len(signals) >= 1
    assert signals[0].alpha_score >= 0
