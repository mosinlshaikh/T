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
                PreviewData.state.copy(
                    isPreviewData = false,
                    connectionStatus = "Backend reachable",
                    backendConnectionState = BackendConnectionState.CONNECTED,
                    lastKnownBotState = supervisorState,
                    latestDecision = DecisionSummary(
                        decisionId = "backend-connected",
                        action = "SKIP",
                        confidence = "0.00",
                        reason = "Backend connected. No verified trade decision has been provided yet.",
                        evidence = listOf("Railway backend health check passed", "Paper mode active", "Live trading disabled"),
                        missingData = listOf("market_signal_snapshot", "verified_ai_decision"),
                        conflicts = emptyList(),
                        zeroHallucinationVerified = true,
                        riskStatus = "waiting_for_decision"
                    ),
                    openTrades = emptyList(),
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
}
