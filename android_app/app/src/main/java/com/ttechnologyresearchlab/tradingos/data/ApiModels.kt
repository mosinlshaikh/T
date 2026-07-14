package com.ttechnologyresearchlab.tradingos.data

import com.ttechnologyresearchlab.tradingos.localization.AppLanguage

enum class BackendConnectionState {
    CONNECTED,
    DISCONNECTED,
    DEGRADED,
    UNKNOWN
}

data class ApiResponse<T>(
    val success: Boolean = false,
    val message: String = "",
    val data: T? = null,
    val timestamp: String = "",
    val requestId: String = "",
    val warnings: List<String> = emptyList(),
    val errors: List<String> = emptyList()
)

data class BotStatus(
    val botState: String = "DEVELOPMENT_PREVIEW",
    val tradingMode: String = "paper",
    val liveTradingEnabled: Boolean = false,
    val apiReadinessStatus: String = "READY_FOR_PAPER",
    val supervisorHealth: Boolean = false,
    val failureState: String = "NONE",
    val lastHeartbeat: Int = 0
)

data class SafetyScoreUi(
    val score: Int = 100,
    val level: String = "SAFE",
    val reasons: List<String> = listOf("DEVELOPMENT PREVIEW DATA"),
    val recommendedAction: String = "Continue paper-only monitoring."
)

data class PortfolioSummary(
    val paperBalanceUsdt: String = "10,000.00",
    val dailyPnl: String = "0.00",
    val openTrades: Int = 0,
    val exposure: String = "0.00",
    val reserveLock: String = "10%",
    val drawdown: String = "0.00%"
)

data class DecisionSummary(
    val decisionId: String = "preview",
    val action: String = "SKIP",
    val confidence: String = "0.00",
    val reason: String = "DEVELOPMENT PREVIEW DATA: backend not connected.",
    val evidence: List<String> = listOf("Evidence-first decision label"),
    val missingData: List<String> = listOf("backend_connection"),
    val conflicts: List<String> = emptyList(),
    val zeroHallucinationVerified: Boolean = false,
    val riskStatus: String = "unknown"
)

data class MarketIntelligenceSummary(
    val candleSignal: String = "unknown",
    val orderBookSignal: String = "unknown",
    val whaleSignal: String = "unknown",
    val newsRiskSignal: String = "unknown",
    val marketStructureSignal: String = "unknown",
    val combinedConfidence: String = "unknown",
    val missingData: List<String> = listOf("backend_connection"),
    val conflicts: List<String> = emptyList()
)

data class TradeRow(
    val id: String,
    val symbol: String,
    val side: String,
    val status: String,
    val pnl: String
)

data class ReportSummary(
    val title: String,
    val status: String,
    val detail: String
)

data class StatementUi(
    val statementId: String = "unknown",
    val windowHours: String = "24",
    val realizedPnl: String = "0.00",
    val unrealizedPnl: String = "0.00",
    val netPnl: String = "0.00",
    val grossProfit: String = "0.00",
    val grossLoss: String = "0.00",
    val winRatePct: String = "0.00",
    val openPositions: String = "0",
    val closedPositions: String = "0",
    val journalEntries: String = "0",
    val safetyChecks: List<String> = emptyList(),
    val tradeRows: List<String> = emptyList(),
    val paperScanRows: List<String> = emptyList(),
    val notes: List<String> = emptyList(),
    val sevenDayNetPnl: String = "0.00",
    val sevenDayRealizedPnl: String = "0.00",
    val sevenDayClosedPositions: String = "0",
    val sevenDayWinRatePct: String = "0.00"
)

data class DerivativesUi(
    val mode: String = "RESEARCH_ONLY",
    val futuresExecutionAvailable: Boolean = false,
    val optionsExecutionAvailable: Boolean = false,
    val leverageExecutionAvailable: Boolean = false,
    val notionalUsdt: String = "100",
    val leverage: String = "2",
    val marginEstimateUsdt: String = "50",
    val estimatedLossUsdt: String = "1",
    val liquidationWarning: String = "Paper-only risk estimate.",
    val blockedReasons: List<String> = emptyList(),
    val allowedFeatures: List<String> = emptyList(),
    val safetyNotes: List<String> = emptyList()
)

data class AuditEventRow(
    val timestamp: String,
    val type: String,
    val detail: String
)

data class RiskSettingsUi(
    val reserveCapitalPct: String = "10%",
    val maxRiskExposurePct: String = "5%",
    val stopLossRequired: Boolean = true,
    val takeProfitRequired: Boolean = true
)

data class AppSettingsUi(
    val backendBaseUrl: String = "https://t-production-8efc.up.railway.app",
    val risk: RiskSettingsUi = RiskSettingsUi(),
    val notifications: String = "placeholders disabled",
    val vaultStatus: String = "placeholder only",
    val liveTradingStatus: String = "BLOCKED / DISABLED",
    val withdrawalsStatus: String = "UNSUPPORTED"
)

data class LicenseStatusUi(
    val status: String = "UNKNOWN",
    val message: String = "DEVELOPMENT PREVIEW DATA",
    val redactedLicenseKey: String = "",
    val expiry: String = "unknown",
    val remainingActivations: String = "unknown",
    val warnings: List<String> = emptyList()
)

data class StrategyCatalogUi(
    val name: String,
    val family: String,
    val purpose: String,
    val requiredData: List<String> = emptyList(),
    val status: String = "PAPER_ADVISORY",
    val safetyRules: List<String> = emptyList()
)

data class PaperSessionUi(
    val running: Boolean = false,
    val sessionId: String = "",
    val startedAt: String = "",
    val symbols: List<String> = emptyList(),
    val timeframe: String = "5m",
    val intervalSeconds: String = "300",
    val scanCount: Int = 0,
    val bestCandidate: String = "unknown",
    val bestAction: String = "unknown",
    val bestConfidence: String = "0.00",
    val lastReason: String = "No paper session scan yet.",
    val autoResumeEnabled: Boolean = false,
    val desiredSymbols: List<String> = emptyList(),
    val publicDataOnly: Boolean = true,
    val liveTradingEnabled: Boolean = false
)

data class DashboardChartsUi(
    val buyCount: Int = 0,
    val sellCount: Int = 0,
    val holdCount: Int = 0,
    val skipCount: Int = 0,
    val highConfidence: Int = 0,
    val mediumConfidence: Int = 0,
    val lowConfidence: Int = 0,
    val averageConfidence: String = "0.00"
)

data class TimelineEventUi(
    val timestamp: String = "unknown",
    val type: String = "paper_event",
    val title: String = "unknown",
    val detail: String = "unknown / insufficient data",
    val status: String = "paper",
    val symbol: String = ""
)

data class MarketEvidenceUi(
    val timestamp: String = "unknown",
    val layer: String = "unknown",
    val signal: String = "unknown",
    val confidence: String = "unknown",
    val summary: String = "unknown / insufficient data",
    val symbol: String = "",
    val source: String = "unknown",
    val missingData: List<String> = emptyList(),
    val conflicts: List<String> = emptyList()
)

data class CandleDetailUi(
    val symbol: String = "BTCUSDT",
    val timeframe: String = "5m",
    val candleCount: Int = 0,
    val trend: String = "unknown",
    val latestClose: String = "unknown",
    val rangeHigh: String = "unknown",
    val rangeLow: String = "unknown",
    val volumeTotal: String = "0.00",
    val source: String = "unknown",
    val missingData: List<String> = listOf("candles"),
    val decisionRule: String = "Missing candle data = SKIP",
    val sparklineCloses: List<String> = emptyList()
)

data class CandleStudyUi(
    val timeframe: String = "unknown",
    val trend: String = "unknown",
    val confidence: String = "0.00",
    val moveReason: String = "Candle study unavailable.",
    val learningNotes: List<String> = emptyList(),
    val missingData: List<String> = emptyList()
)

data class PaperScanSummaryUi(
    val symbol: String = "unknown",
    val timeframe: String = "unknown",
    val action: String = "unknown",
    val status: String = "unknown",
    val confidence: String = "0.00",
    val reason: String = "No paper scan result available.",
    val whyNotTraded: String = "No paper trade was opened by policy.",
    val timestamp: String = "unknown",
    val runCount: Int = 0,
    val tradeAllowed: Boolean = false
)

data class PaperScanHistoryRowUi(
    val timestamp: String = "unknown",
    val symbol: String = "UNKNOWN",
    val timeframe: String = "",
    val action: String = "SKIP",
    val status: String = "SKIP",
    val confidence: String = "0.00",
    val tradeAllowed: Boolean = false,
    val whyNotTraded: String = "No paper trade was opened by policy.",
    val strategyBreakdown: List<String> = emptyList(),
    val source: String = "paper_scan"
)

data class PaperDemoReadinessUi(
    val monitoringPercent: Int = 0,
    val demoPercent: Int = 0,
    val readyForPaperDemo: Boolean = false,
    val remaining: List<String> = emptyList()
)

data class PerformanceWheelSegmentUi(
    val name: String = "unknown",
    val score: Int = 0,
    val status: String = "UNKNOWN"
)

data class PerformanceWheelUi(
    val overallScore: Int = 0,
    val segments: List<PerformanceWheelSegmentUi> = emptyList(),
    val netPnl: String = "0.00"
)

data class TradeQualityUi(
    val score: Int = 0,
    val level: String = "UNKNOWN",
    val recommendedAction: String = "SKIP",
    val tradeAllowed: Boolean = false,
    val reason: String = "Trade quality unavailable.",
    val latestSymbol: String = "unknown",
    val latestTimestamp: String = "unknown",
    val evidenceSymbolAligned: Boolean = false,
    val warnings: List<String> = emptyList(),
    val missingData: List<String> = emptyList(),
    val conflicts: List<String> = emptyList()
)

data class NoTradeZoneUi(
    val active: Boolean = true,
    val zone: String = "NO_TRADE",
    val recommendedAction: String = "SKIP",
    val reasons: List<String> = listOf("backend_connection")
)

data class ShadowModeUi(
    val enabled: Boolean = true,
    val mode: String = "PAPER_SHADOW_ONLY",
    val wouldDo: String = "SKIP",
    val reason: String = "Shadow mode unavailable.",
    val noTradeZoneActive: Boolean = true
)

data class CoinUniverseUi(
    val mode: String = "ALL_ACTIVE_USDT_SPOT",
    val symbolCount: Int = 0,
    val scanBatchLimit: Int = 0,
    val symbolsPreview: List<String> = emptyList(),
    val rule: String = "Coin universe unavailable."
)

data class DailyTargetUi(
    val targetPnlPct: String = "10",
    val targetAmountUsdt: String = "0.00",
    val currentDailyPnlUsdt: String = "0.00",
    val progressPct: String = "0.00",
    val targetReached: Boolean = false,
    val recommendedMode: String = "PAPER_DISCOVERY",
    val rules: List<String> = emptyList()
)

data class OfflineSyncUi(
    val status: String = "UNKNOWN",
    val lastSuccessfulSync: String = "unknown",
    val queuedLocalActions: Int = 0,
    val cacheStatus: String = "DEVELOPMENT PREVIEW DATA"
)

data class TradingOsUiState(
    val isPreviewData: Boolean = true,
    val backendBaseUrl: String = "https://t-production-8efc.up.railway.app",
    val connectionStatus: String = "DEVELOPMENT PREVIEW DATA",
    val backendConnectionState: BackendConnectionState = BackendConnectionState.UNKNOWN,
    val lastKnownBotState: String = "unknown",
    val lastHeartbeat: String = "unknown",
    val language: AppLanguage = AppLanguage.English,
    val appLocked: Boolean = false,
    val onboardingComplete: Boolean = false,
    val botStatus: BotStatus = BotStatus(),
    val safetyScore: SafetyScoreUi = SafetyScoreUi(),
    val portfolio: PortfolioSummary = PortfolioSummary(),
    val latestDecision: DecisionSummary = DecisionSummary(),
    val marketIntelligence: MarketIntelligenceSummary = MarketIntelligenceSummary(),
    val openTrades: List<TradeRow> = emptyList(),
    val closedTrades: List<TradeRow> = emptyList(),
    val journal: List<TradeRow> = emptyList(),
    val reports: List<ReportSummary> = emptyList(),
    val statement: StatementUi = StatementUi(),
    val derivatives: DerivativesUi = DerivativesUi(),
    val auditEvents: List<AuditEventRow> = emptyList(),
    val settings: AppSettingsUi = AppSettingsUi(),
    val licenseStatus: LicenseStatusUi = LicenseStatusUi(),
    val strategyCatalog: List<StrategyCatalogUi> = emptyList(),
    val paperSession: PaperSessionUi = PaperSessionUi(),
    val dashboardCharts: DashboardChartsUi = DashboardChartsUi(),
    val decisionTimeline: List<TimelineEventUi> = emptyList(),
    val tradeTimeline: List<TimelineEventUi> = emptyList(),
    val auditTimeline: List<TimelineEventUi> = emptyList(),
    val marketEvidenceFeed: List<MarketEvidenceUi> = emptyList(),
    val candleDetail: CandleDetailUi = CandleDetailUi(),
    val candleStudies: List<CandleStudyUi> = emptyList(),
    val paperScanSummary: PaperScanSummaryUi = PaperScanSummaryUi(),
    val paperScanHistory: List<PaperScanHistoryRowUi> = emptyList(),
    val paperDemoReadiness: PaperDemoReadinessUi = PaperDemoReadinessUi(),
    val performanceWheel: PerformanceWheelUi = PerformanceWheelUi(),
    val tradeQuality: TradeQualityUi = TradeQualityUi(),
    val noTradeZone: NoTradeZoneUi = NoTradeZoneUi(),
    val shadowMode: ShadowModeUi = ShadowModeUi(),
    val coinUniverse: CoinUniverseUi = CoinUniverseUi(),
    val dailyTarget: DailyTargetUi = DailyTargetUi(),
    val offlineSync: OfflineSyncUi = OfflineSyncUi(),
    val shutdownState: String = "RUNNING"
)
