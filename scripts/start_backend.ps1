param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8000
)

$env:TRADING_MODE = if ($env:TRADING_MODE) { $env:TRADING_MODE } else { "paper" }
$env:LIVE_TRADING_ENABLED = "false"
$env:MANUAL_LIVE_UNLOCK = "false"
$env:BINANCE_WITHDRAWALS_SUPPORTED = "false"

python -m uvicorn trading_os.api.app:app --host $HostName --port $Port
