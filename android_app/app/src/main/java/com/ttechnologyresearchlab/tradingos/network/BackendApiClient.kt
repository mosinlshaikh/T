package com.ttechnologyresearchlab.tradingos.network

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.HttpURLConnection
import java.net.SocketTimeoutException
import java.net.URL

data class ApiClientResult(
    val ok: Boolean,
    val body: String = "",
    val safeError: String = ""
)

class BackendApiClient(
    private val baseUrlProvider: () -> String
) {
    var lastKnownBody: String = ""
        private set

    suspend fun getBotStatus() = get("/status/bot")
    suspend fun getHealth() = get("/status/health")
    suspend fun getBinanceReadiness() = get("/status/binance-readiness")
    suspend fun getRealWorldReadiness() = get("/status/real-world-readiness")
    suspend fun getShutdown() = get("/status/shutdown")
    suspend fun getRuntimeStatus() = get("/status/runtime")
    suspend fun getPortfolioSummary() = get("/portfolio/summary")
    suspend fun getWallet() = get("/portfolio/wallet")
    suspend fun getOpenPositions() = get("/portfolio/open-positions")
    suspend fun getClosedPositions() = get("/portfolio/closed-positions")
    suspend fun getPortfolioPnl() = get("/portfolio/pnl")
    suspend fun getPortfolioExposure() = get("/portfolio/exposure")
    suspend fun getOpenTrades() = get("/trades/open")
    suspend fun getClosedTrades() = get("/trades/closed")
    suspend fun getLatestTrade() = get("/trades/latest")
    suspend fun getTradeJournal() = get("/trades/journal")
    suspend fun getTrade(tradeId: String) = get("/trades/$tradeId")
    suspend fun getLatestDecision() = get("/decisions/latest")
    suspend fun getDecisionHistory() = get("/decisions/history")
    suspend fun getDecision(decisionId: String) = get("/decisions/$decisionId")
    suspend fun getSkippedDecisions() = get("/decisions/skipped")
    suspend fun getBlockedDecisions() = get("/decisions/blocked")
    suspend fun getLatestAudit() = get("/audit/latest")
    suspend fun getAuditEvents() = get("/audit/events")
    suspend fun getAuditErrors() = get("/audit/errors")
    suspend fun getAuditSecurity() = get("/audit/security")
    suspend fun getAuditRuntime() = get("/audit/runtime")
    suspend fun getDailyReport() = get("/reports/daily")
    suspend fun getStatementReport() = get("/reports/statement-daily")
    suspend fun getSevenDayStatementReport() = get("/reports/statement-7d")
    suspend fun getWeeklyReport() = get("/reports/weekly")
    suspend fun getMonthlyReport() = get("/reports/monthly")
    suspend fun getPerformanceReport() = get("/reports/performance")
    suspend fun getRiskReport() = get("/reports/risk")
    suspend fun getHallucinationReport() = get("/reports/hallucination")
    suspend fun getSkippedTradeReport() = get("/reports/skipped-trades")
    suspend fun getStrategyReport() = get("/reports/strategies")
    suspend fun getRuntimeReport() = get("/reports/runtime")
    suspend fun getDashboardCharts() = get("/reports/dashboard-charts")
    suspend fun getDashboardTimelines() = get("/reports/timelines")
    suspend fun getLocalAiLearning() = get("/learning/local-ai")
    suspend fun getMarketKingScore() = get("/learning/market-king-score")
    suspend fun getLearningRecommendations() = get("/learning/recommendations")
    suspend fun getDerivativesReadiness() = get("/derivatives/readiness")
    suspend fun getDerivativesRiskEstimate() = get("/derivatives/risk-estimate?symbol=BTCUSDT&instrument=FUTURES&notional_usdt=100&leverage=2&adverse_move_pct=1")
    suspend fun getPaperLiveMonitor() = get("/monitor/paper-live")
    suspend fun getMarketEvidenceFeed() = get("/monitor/market-evidence")
    suspend fun getCandleDetail() = get("/monitor/candle-detail?symbol=BTCUSDT&timeframe=5m&limit=40")
    suspend fun getCandleStudy() = get("/monitor/candle-study?symbol=BTCUSDT&timeframes=5m,10m,1h,4h,8h,24h,1M&limit=80")
    suspend fun getPaperScanSummary() = get("/monitor/paper-scan-summary")
    suspend fun getPaperScanHistory() = get("/monitor/paper-scan-history?limit=20")
    suspend fun getWatchlistCandidates() = get("/monitor/watchlist-candidates?limit=10")
    suspend fun getPaperDemoReadiness() = get("/monitor/paper-demo-readiness")
    suspend fun getPerformanceWheel() = get("/monitor/performance-wheel")
    suspend fun getTradeQuality() = get("/monitor/trade-quality")
    suspend fun getNoTradeZone() = get("/monitor/no-trade-zone")
    suspend fun getStrategyBlockers() = get("/monitor/strategy-blockers?limit=100")
    suspend fun getShadowMode() = get("/monitor/shadow-mode")
    suspend fun getSymbolUniverse() = get("/monitor/symbol-universe?max_preview=80")
    suspend fun getMarketRadar() = get("/monitor/market-radar?limit=30")
    suspend fun getFastMarketState() = get("/monitor/fast-market-state?limit=30")
    suspend fun getDailyTarget() = get("/monitor/daily-target?target_pnl_pct=10")
    suspend fun startBot() = post("/control/start")
    suspend fun stopGraceful() = post("/control/stop-graceful")
    suspend fun emergencyStop() = post("/control/emergency-stop")
    suspend fun pauseNewTrades() = post("/control/pause-new-trades")
    suspend fun resumePaperTrades() = post("/control/resume-paper-trades")
    suspend fun runLiveMarketPaperDemo() = post("/control/run-live-market-paper-demo")
    suspend fun runRadarPaperScan() = post("/control/paper-auto-trader/scan-radar?max_symbols=20")
    suspend fun openManualPaperDemo() = post("/control/manual-paper-demo/open?symbol=BTCUSDT&trade_notional_usdt=25")
    suspend fun closeManualPaperDemo() = post("/control/manual-paper-demo/close-market")
    suspend fun simulateManualStopLoss() = post("/control/manual-paper-demo/simulate-stop-loss")
    suspend fun simulateManualTakeProfit() = post("/control/manual-paper-demo/simulate-take-profit")
    suspend fun startPaperSession() = post("/control/paper-session/start")
    suspend fun stopPaperSession() = post("/control/paper-session/stop")
    suspend fun getPaperSessionStatus() = get("/control/paper-session/status")
    suspend fun getRiskSettings() = get("/settings/risk")
    suspend fun getStrategySettings() = get("/settings/strategy")
    suspend fun getStrategyCatalog() = get("/settings/strategy-catalog")
    suspend fun getSecuritySettings() = get("/settings/security")
    suspend fun getNotificationSettings() = get("/settings/notifications")
    suspend fun validateLicense(licenseKey: String) = postJson(
        "/license/validate",
        """{"license_key":"${jsonEscape(licenseKey)}","package_name":"com.ttechnologyresearchlab.tradingos"}"""
    )

    private suspend fun get(path: String): ApiClientResult = request("GET", path)
    private suspend fun post(path: String): ApiClientResult = request("POST", path)
    private suspend fun postJson(path: String, body: String): ApiClientResult = request("POST", path, body)

    private suspend fun request(method: String, path: String, body: String? = null): ApiClientResult = withContext(Dispatchers.IO) {
        try {
            val base = baseUrlProvider().trimEnd('/')
            val connection = URL("$base$path").openConnection() as HttpURLConnection
            connection.requestMethod = method
            connection.connectTimeout = 15_000
            connection.readTimeout = 15_000
            connection.setRequestProperty("Accept", "application/json")
            if (body != null) {
                connection.doOutput = true
                connection.setRequestProperty("Content-Type", "application/json")
                connection.outputStream.use { stream ->
                    stream.write(body.toByteArray(Charsets.UTF_8))
                }
            }
            val body = connection.inputStream.bufferedReader().use { it.readText() }
            lastKnownBody = body
            ApiClientResult(ok = true, body = body)
        } catch (_: SocketTimeoutException) {
            ApiClientResult(ok = false, safeError = "Backend timeout. Offline mode active.")
        } catch (_: Exception) {
            ApiClientResult(ok = false, safeError = "Backend unavailable. Preview data shown.")
        }
    }

    private fun jsonEscape(value: String): String {
        return value
            .replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\n", "")
            .replace("\r", "")
            .trim()
    }
}
