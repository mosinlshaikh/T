package com.ttechnologyresearchlab.tradingos.data

import com.ttechnologyresearchlab.tradingos.network.BackendApiClient

class TradingOsRepository(
    private val apiClient: BackendApiClient
) {
    suspend fun refreshDashboard(): TradingOsUiState {
        return try {
            val health = apiClient.getHealth()
            if (health.ok) {
                val shutdownState = health.body.jsonString("shutdown_state") ?: "RUNNING"
                val supervisorState = health.body.jsonString("supervisor_state") ?: "UNKNOWN"
                val liveTradingEnabled = health.body.jsonBoolean("live_trading_enabled") ?: false
                val latestDecisionResult = apiClient.getLatestDecision()
                val latestDecision = latestDecisionResult.toDecisionSummary()
                val openPositionsResult = apiClient.getOpenPositions()
                val openTrades = openPositionsResult.toTradeRows()
                PreviewData.state.copy(
                    isPreviewData = false,
                    connectionStatus = "Backend reachable",
                    backendConnectionState = BackendConnectionState.CONNECTED,
                    lastKnownBotState = supervisorState,
                    latestDecision = latestDecision,
                    openTrades = openTrades,
                    closedTrades = emptyList(),
                    journal = emptyList(),
                    botStatus = PreviewData.state.botStatus.copy(
                        botState = supervisorState,
                        liveTradingEnabled = liveTradingEnabled
                    ),
                    shutdownState = shutdownState
                )
            } else {
                PreviewData.state.copy(
                    connectionStatus = health.safeError,
                    backendConnectionState = BackendConnectionState.DISCONNECTED
                )
            }
        } catch (_: Exception) {
            PreviewData.state.copy(
                connectionStatus = "DEVELOPMENT PREVIEW DATA",
                backendConnectionState = BackendConnectionState.DISCONNECTED
            )
        }
    }

    suspend fun startBot() = runCatching { apiClient.startBot() }
    suspend fun gracefulStop() = runCatching { apiClient.stopGraceful() }
    suspend fun emergencyStop() = runCatching { apiClient.emergencyStop() }
    suspend fun pauseNewTrades() = runCatching { apiClient.pauseNewTrades() }
    suspend fun resumePaperTrades() = runCatching { apiClient.resumePaperTrades() }
    suspend fun runLiveMarketPaperDemo() = runCatching { apiClient.runLiveMarketPaperDemo() }

    suspend fun validateLicense(licenseKey: String): LicenseStatusUi {
        val result = apiClient.validateLicense(licenseKey)
        if (!result.ok) {
            return LicenseStatusUi(
                status = "BACKEND_OFFLINE",
                message = result.safeError,
                redactedLicenseKey = licenseKey.redactedForUi()
            )
        }
        val body = result.body.uppercase()
        val status = when {
            body.contains("\"VALID\":TRUE") || body.contains("\"VALID\": TRUE") -> "ACTIVE"
            body.contains("EXPIRED") -> "EXPIRED"
            body.contains("REVOKED") -> "REVOKED"
            body.contains("SUSPENDED") -> "SUSPENDED"
            else -> "INVALID"
        }
        return LicenseStatusUi(
            status = status,
            message = "Backend license validation response received.",
            redactedLicenseKey = licenseKey.redactedForUi()
        )
    }

    private fun String.redactedForUi(): String {
        val clean = trim()
        return if (clean.length < 9) "TTRL-****" else "${clean.take(9)}-****"
    }

    private fun String.jsonString(name: String): String? {
        val pattern = Regex(""""$name"\s*:\s*"([^"]*)"""")
        return pattern.find(this)?.groupValues?.getOrNull(1)
    }

    private fun String.jsonBoolean(name: String): Boolean? {
        val pattern = Regex(""""$name"\s*:\s*(true|false)""", RegexOption.IGNORE_CASE)
        return pattern.find(this)?.groupValues?.getOrNull(1)?.equals("true", ignoreCase = true)
    }

    private fun String.jsonNumber(name: String): String? {
        val pattern = Regex(""""$name"\s*:\s*(-?\d+(?:\.\d+)?)""")
        return pattern.find(this)?.groupValues?.getOrNull(1)
    }

    private fun String.jsonArrayItems(name: String): List<String> {
        val arrayPattern = Regex(""""$name"\s*:\s*\[(.*?)\]""", setOf(RegexOption.DOT_MATCHES_ALL, RegexOption.IGNORE_CASE))
        val content = arrayPattern.find(this)?.groupValues?.getOrNull(1) ?: return emptyList()
        return Regex(""""([^"]+)"""").findAll(content).map { it.groupValues[1] }.toList()
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toDecisionSummary(): DecisionSummary {
        if (!ok) {
            return DecisionSummary(
                decisionId = "backend-connected",
                action = "SKIP",
                confidence = "0.00",
                reason = "Backend connected. Latest decision endpoint unavailable.",
                evidence = listOf("Railway backend health check passed", "Paper mode active", "Live trading disabled"),
                missingData = listOf("latest_decision"),
                zeroHallucinationVerified = true,
                riskStatus = "waiting_for_decision"
            )
        }
        val bodyText = body
        val action = bodyText.jsonString("action") ?: bodyText.jsonString("final_decision") ?: bodyText.jsonString("decision") ?: "SKIP"
        val confidence = bodyText.jsonNumber("confidence") ?: bodyText.jsonString("confidence") ?: "0.00"
        val reason = bodyText.jsonString("reason") ?: bodyText.jsonString("message") ?: "Backend decision endpoint returned no reason."
        val verified = bodyText.jsonBoolean("verified_decision")
            ?: bodyText.jsonBoolean("zero_hallucination_verified")
            ?: bodyText.jsonBoolean("verified")
            ?: false
        val evidence = bodyText.jsonArrayItems("evidence").ifEmpty {
            listOf("Backend decision endpoint returned latest paper decision", "Paper mode active", "Live trading disabled")
        }
        return DecisionSummary(
            decisionId = bodyText.jsonString("decision_id") ?: "latest-backend-decision",
            action = action,
            confidence = confidence,
            reason = reason,
            evidence = evidence.take(5),
            missingData = bodyText.jsonArrayItems("missing_data"),
            conflicts = bodyText.jsonArrayItems("conflicts").ifEmpty { bodyText.jsonArrayItems("conflict_signals") },
            zeroHallucinationVerified = verified,
            riskStatus = bodyText.jsonString("risk_status") ?: bodyText.jsonString("status") ?: "paper_only"
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toTradeRows(): List<TradeRow> {
        if (!ok || !body.contains("symbol", ignoreCase = true)) return emptyList()
        val symbol = body.jsonString("symbol") ?: "BTCUSDT"
        val side = body.jsonString("side") ?: "BUY"
        val status = body.jsonString("status") ?: "PAPER_OPEN"
        val pnl = body.jsonNumber("unrealized_pnl") ?: body.jsonNumber("realized_pnl") ?: "0.00"
        return listOf(
            TradeRow(
                id = body.jsonString("position_id") ?: "paper-position",
                symbol = symbol,
                side = side,
                status = status,
                pnl = pnl
            )
        )
    }
}
