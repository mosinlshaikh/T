from __future__ import annotations

from dataclasses import dataclass, field

from trading_os.ai.decision_brain import AIDecisionBrain
from trading_os.ai.verified_decision_engine import VerifiedDecisionEngine
from trading_os.audit.audit_logger import AuditLogger
from trading_os.binance.spot_knowledge import BinanceSpotKnowledgeEngine
from trading_os.config import TradingOSConfig
from trading_os.connectors.binance_spot import BinanceSpotConnector
from trading_os.connectors.rest_api import RestApiConnector
from trading_os.connectors.websocket_market_data import WebSocketMarketDataConnector
from trading_os.execution.intent import ExecutionIntentLayer
from trading_os.db.repository import TradingOSRepository
from trading_os.intelligence.candle_intelligence import CandleIntelligenceEngine
from trading_os.intelligence.news_intelligence import NewsIntelligenceEngine
from trading_os.intelligence.news_risk_intelligence import NewsRiskIntelligenceEngine
from trading_os.intelligence.order_book_intelligence import OrderBookIntelligenceEngine
from trading_os.intelligence.market_structure import MarketStructureEngine
from trading_os.intelligence.signal_combiner import MultiFactorSignalCombiner
from trading_os.intelligence.whale_intelligence import WhaleIntelligenceEngine
from trading_os.intelligence.whale_intelligence_v1 import WhaleIntelligenceV1
from trading_os.market.candle_engine import CandleEngine
from trading_os.market.market_data_engine import MarketDataEngine, VolumeSpikeDetector
from trading_os.market.mini_ticker_stream import BinanceMiniTickerStream
from trading_os.market.order_book_engine import OrderBookEngine
from trading_os.market.stream_state import MarketStreamState
from trading_os.notifications.engine import NotificationEngine
from trading_os.paper.simulator import PaperTradingSimulator
from trading_os.pipeline.decision_to_trade import DecisionToTradePipeline
from trading_os.portfolio.state import PortfolioStateManager
from trading_os.risk.capital_manager import CapitalManager
from trading_os.risk.risk_engine import RiskEngine
from trading_os.runtime.supervisor import RuntimeSupervisor
from trading_os.runtime.shutdown_engine import SmartShutdownEngine
from trading_os.runtime.paper_auto_trader import PaperAutoTrader
from trading_os.runtime.paper_session_scheduler import PaperSessionScheduler
from trading_os.security.api_key_vault import ApiKeyVaultDesign
from trading_os.security.kill_switch import EmergencyKillSwitch
from trading_os.security.permission_verifier import BinanceApiPermissionVerifier
from trading_os.strategies.registry import StrategyRegistry
from trading_os.trade.lifecycle import TradeLifecycleEngine


@dataclass
class TradingOSBackend:
    config: TradingOSConfig = field(default_factory=TradingOSConfig)
    binance_spot: BinanceSpotConnector = field(init=False)
    binance_knowledge: BinanceSpotKnowledgeEngine = field(init=False)
    rest_api: RestApiConnector = field(init=False)
    websocket_market_data: WebSocketMarketDataConnector = field(init=False)
    market_data: MarketDataEngine = field(init=False)
    market_stream_state: MarketStreamState = field(init=False)
    mini_ticker_stream: BinanceMiniTickerStream = field(init=False)
    candle_engine: CandleEngine = field(init=False)
    order_book_engine: OrderBookEngine = field(init=False)
    volume_spike_detector: VolumeSpikeDetector = field(init=False)
    ai_brain: AIDecisionBrain = field(init=False)
    verified_decisions: VerifiedDecisionEngine = field(init=False)
    whale_intelligence: WhaleIntelligenceEngine = field(init=False)
    whale_intelligence_v1: WhaleIntelligenceV1 = field(init=False)
    news_intelligence: NewsIntelligenceEngine = field(init=False)
    news_risk_intelligence: NewsRiskIntelligenceEngine = field(init=False)
    candle_intelligence: CandleIntelligenceEngine = field(init=False)
    order_book_intelligence: OrderBookIntelligenceEngine = field(init=False)
    market_structure: MarketStructureEngine = field(init=False)
    signal_combiner: MultiFactorSignalCombiner = field(init=False)
    repository: TradingOSRepository = field(init=False)
    risk_engine: RiskEngine = field(init=False)
    capital_manager: CapitalManager = field(init=False)
    portfolio: PortfolioStateManager = field(init=False)
    paper_simulator: PaperTradingSimulator = field(init=False)
    strategies: StrategyRegistry = field(init=False)
    lifecycle: TradeLifecycleEngine = field(init=False)
    intent_layer: ExecutionIntentLayer = field(init=False)
    decision_to_trade_pipeline: DecisionToTradePipeline = field(init=False)
    audit_logger: AuditLogger = field(init=False)
    kill_switch: EmergencyKillSwitch = field(init=False)
    shutdown_engine: SmartShutdownEngine = field(init=False)
    api_vault: ApiKeyVaultDesign = field(init=False)
    permission_verifier: BinanceApiPermissionVerifier = field(init=False)
    runtime_supervisor: RuntimeSupervisor = field(init=False)
    paper_auto_trader: PaperAutoTrader = field(init=False)
    paper_session_scheduler: PaperSessionScheduler = field(init=False)
    notifications: NotificationEngine = field(init=False)

    def __post_init__(self) -> None:
        self.config.assert_safe()
        self.repository = TradingOSRepository.from_database_url(self.config.database_url)
        self.kill_switch = EmergencyKillSwitch()
        self.shutdown_engine = SmartShutdownEngine()
        self.audit_logger = AuditLogger(path=self.config.audit_log_path, repository=self.repository)
        self.api_vault = ApiKeyVaultDesign()
        self.permission_verifier = BinanceApiPermissionVerifier()
        self.runtime_supervisor = RuntimeSupervisor(
            config=self.config,
            vault=self.api_vault,
            permission_verifier=self.permission_verifier,
            shutdown=self.shutdown_engine,
            audit=self.audit_logger,
            repository=self.repository,
        )
        self.notifications = NotificationEngine(audit=self.audit_logger)
        self.rest_api = RestApiConnector()
        self.websocket_market_data = WebSocketMarketDataConnector()
        self.binance_knowledge = BinanceSpotKnowledgeEngine()
        self.binance_spot = BinanceSpotConnector(
            rest_api=self.rest_api,
            websocket_market_data=self.websocket_market_data,
            live_trading_enabled=self.config.enable_live_trading,
        )
        self.market_data = MarketDataEngine()
        self.market_stream_state = MarketStreamState()
        self.mini_ticker_stream = BinanceMiniTickerStream(self.market_stream_state)
        self.candle_engine = CandleEngine()
        self.order_book_engine = OrderBookEngine()
        self.volume_spike_detector = VolumeSpikeDetector()
        self.ai_brain = AIDecisionBrain()
        self.verified_decisions = VerifiedDecisionEngine()
        self.whale_intelligence = WhaleIntelligenceEngine()
        self.whale_intelligence_v1 = WhaleIntelligenceV1()
        self.news_intelligence = NewsIntelligenceEngine()
        self.news_risk_intelligence = NewsRiskIntelligenceEngine()
        self.candle_intelligence = CandleIntelligenceEngine()
        self.order_book_intelligence = OrderBookIntelligenceEngine()
        self.market_structure = MarketStructureEngine()
        self.signal_combiner = MultiFactorSignalCombiner()
        self.risk_engine = RiskEngine()
        self.capital_manager = CapitalManager()
        self.portfolio = PortfolioStateManager()
        self.paper_simulator = PaperTradingSimulator(
            portfolio=self.portfolio, repository=self.repository
        )
        self.strategies = StrategyRegistry.with_default_placeholders()
        self.lifecycle = TradeLifecycleEngine()
        self.intent_layer = ExecutionIntentLayer(live_enabled=False)
        self.decision_to_trade_pipeline = DecisionToTradePipeline(
            strategies=self.strategies,
            ai_brain=self.ai_brain,
            verifier=self.verified_decisions,
            risk_engine=self.risk_engine,
            capital_manager=self.capital_manager,
            intent_layer=self.intent_layer,
            paper_simulator=self.paper_simulator,
            lifecycle=self.lifecycle,
            shutdown=self.shutdown_engine,
            audit=self.audit_logger,
            candle_intelligence=self.candle_intelligence,
            order_book_intelligence=self.order_book_intelligence,
            whale_intelligence=self.whale_intelligence_v1,
            news_risk_intelligence=self.news_risk_intelligence,
            market_structure=self.market_structure,
            signal_combiner=self.signal_combiner,
        )
        self.paper_auto_trader = PaperAutoTrader(self)
        self.paper_session_scheduler = PaperSessionScheduler(self)

    def health(self) -> dict[str, object]:
        config_health = self.config.health_report()
        vault_health = self.api_vault.health_report()
        api_readiness = self.permission_verifier.verify(self.config, self.api_vault)
        wallet = self.portfolio.wallet_snapshot()
        return {
            "system": "T Trading OS Backend",
            "mode": self.config.runtime_mode.value,
            "live_trading_enabled": self.config.enable_live_trading,
            "withdraw_permissions_supported": self.config.allow_withdraw_permissions,
            "kill_switch_active": self.kill_switch.active,
            "shutdown_state": self.shutdown_engine.state.value,
            "supervisor_state": self.runtime_supervisor.state.value,
            "supervisor_healthy": self.runtime_supervisor.healthy,
            "last_heartbeat": self.runtime_supervisor.last_heartbeat_at or "NOT_STARTED",
            "last_heartbeat_count": self.runtime_supervisor.heartbeat_count,
            "failure_state": self.runtime_supervisor.failure_state.value,
            "config_status": config_health,
            "vault_status": vault_health,
            "binance_readiness_status": {
                "status": api_readiness.status.value,
                "ready": api_readiness.ready,
                "reasons": api_readiness.reasons,
            },
            "portfolio_summary": {
                "wallet": {
                    "usdt_balance": wallet.usdt_balance,
                    "reserved_capital": wallet.reserved_capital,
                    "realized_pnl": wallet.realized_pnl,
                    "unrealized_pnl": wallet.unrealized_pnl,
                },
                "open_positions": len(self.portfolio.open_positions),
                "closed_positions": len(self.portfolio.closed_positions),
                "exposure": self.portfolio.exposure(),
                "available_capital": self.portfolio.available_capital(),
                "daily_pnl": self.portfolio.daily_pnl(),
                "drawdown_pct": self.portfolio.drawdown_pct(),
            },
            "open_paper_positions": len(self.portfolio.open_positions),
            "status": "ok" if not self.kill_switch.active else "halted",
        }
