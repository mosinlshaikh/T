"""AI Binance Trading OS backend foundation.

This package is intentionally execution-safe by default:
- paper/sandbox mode is the default runtime mode
- live trading execution is disabled
- withdraw permissions are not supported
- AI decisions must be backed by data evidence
"""

from trading_os.config import TradingOSConfig
from trading_os.orchestrator import TradingOSBackend

__all__ = ["TradingOSBackend", "TradingOSConfig"]
