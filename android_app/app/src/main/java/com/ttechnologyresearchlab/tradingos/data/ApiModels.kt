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
    val symbols: List<String> = emptyList(),
    val timeframe: String = "5m",
    val intervalSeconds: String = "300",
    val scanCount: Int = 0,
    val bestCandidate: String = "unknown",
    val bestAction: String = "unknown",
    val bestConfidence: String = "0.00",
    val lastReason: String = "No paper session scan yet.",
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
    val auditEvents: List<AuditEventRow> = emptyList(),
    val settings: AppSettingsUi = AppSettingsUi(),
    val licenseStatus: LicenseStatusUi = LicenseStatusUi(),
    val strategyCatalog: List<StrategyCatalogUi> = emptyList(),
    val paperSession: PaperSessionUi = PaperSessionUi(),
    val dashboardCharts: DashboardChartsUi = DashboardChartsUi(),
    val shutdownState: String = "RUNNING"
)
