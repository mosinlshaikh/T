use std::env;
use std::process;

fn truthy(name: &str) -> bool {
    matches!(
        env::var(name).unwrap_or_default().to_lowercase().as_str(),
        "1" | "true" | "yes" | "live"
    )
}

fn main() {
    let trading_mode = env::var("TRADING_MODE").unwrap_or_else(|_| "paper".to_string());
    let live_enabled = truthy("LIVE_TRADING_ENABLED");
    let manual_live_unlock = truthy("MANUAL_LIVE_UNLOCK");
    let withdrawals_supported = truthy("BINANCE_WITHDRAWALS_SUPPORTED");

    if trading_mode.to_lowercase() != "paper" {
        eprintln!("safety_guard=blocked reason=TRADING_MODE_must_remain_paper");
        process::exit(2);
    }
    if live_enabled || manual_live_unlock {
        eprintln!("safety_guard=blocked reason=live_trading_flags_must_remain_false");
        process::exit(3);
    }
    if withdrawals_supported {
        eprintln!("safety_guard=blocked reason=withdrawals_must_remain_unsupported");
        process::exit(4);
    }

    println!("safety_guard=ok mode=paper live_trading=false withdrawals=false");
}
