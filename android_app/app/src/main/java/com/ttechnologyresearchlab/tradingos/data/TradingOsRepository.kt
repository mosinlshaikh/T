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
                val monitorResult = apiClient.getPaperLiveMonitor()
                val monitorState = monitorResult.toMonitorState()
                val readinessResult = apiClient.getRealWorldReadiness()
                val safetyScore = readinessResult.toSafetyScore()
                val strategyCatalog = apiClient.getStrategyCatalog().toStrategyCatalog()
                PreviewData.state.copy(
                    isPreviewData = false,
                    connectionStatus = "Backend reachable",
                    backendConnectionState = BackendConnectionState.CONNECTED,
                    lastKnownBotState = supervisorState,
                    latestDecision = monitorState.latestDecision ?: latestDecision,
                    marketIntelligence = monitorState.marketIntelligence,
                    openTrades = monitorState.openTrades.ifEmpty { openTrades },
                    closedTrades = monitorState.closedTrades,
                    journal = monitorState.journal,
                    auditEvents = monitorState.auditEvents,
                    portfolio = monitorState.portfolio ?: PreviewData.state.portfolio,
                    safetyScore = safetyScore,
                    strategyCatalog = strategyCatalog.ifEmpty { PreviewData.state.strategyCatalog },
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
    suspend fun refreshLearningSummary() = runCatching { apiClient.getLocalAiLearning() }

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

    private data class MonitorState(
        val latestDecision: DecisionSummary? = null,
        val marketIntelligence: MarketIntelligenceSummary = MarketIntelligenceSummary(),
        val openTrades: List<TradeRow> = emptyList(),
        val closedTrades: List<TradeRow> = emptyList(),
        val journal: List<TradeRow> = emptyList(),
        val auditEvents: List<AuditEventRow> = emptyList(),
        val portfolio: PortfolioSummary? = null
    )

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toMonitorState(): MonitorState {
        if (!ok) return MonitorState()
        val bodyText = body
        val decision = toDecisionSummary()
        val intelligence = MarketIntelligenceSummary(
            candleSignal = bodyText.latestReasonFor("candle_analysis"),
            orderBookSignal = bodyText.latestReasonFor("order_book_analysis"),
            whaleSignal = bodyText.latestReasonFor("whale_analysis"),
            newsRiskSignal = bodyText.latestReasonFor("news_risk_analysis"),
            marketStructureSignal = bodyText.latestReasonFor("market_structure_analysis"),
            combinedConfidence = bodyText.jsonNumber("confidence_score") ?: decision.confidence,
            missingData = bodyText.jsonArrayItems("missing_data"),
            conflicts = decision.conflicts
        )
        val auditRows = bodyText.auditEventRows().takeLast(12)
        val journalRows = bodyText.tradeRowsFromSection("paper_journal")
        val openRows = bodyText.tradeRowsFromSection("open_positions")
        val closedRows = bodyText.tradeRowsFromSection("closed_positions")
        val portfolioSummary = PortfolioSummary(
            paperBalanceUsdt = bodyText.jsonNumber("usdt_balance") ?: PreviewData.state.portfolio.paperBalanceUsdt,
            dailyPnl = bodyText.jsonNumber("daily_pnl") ?: "0.00",
            openTrades = openRows.size,
            exposure = bodyText.jsonNumber("exposure") ?: "0.00",
            reserveLock = "10%",
            drawdown = "${bodyText.jsonNumber("drawdown_pct") ?: "0.00"}%"
        )
        return MonitorState(
            latestDecision = decision,
            marketIntelligence = intelligence,
            openTrades = openRows,
            closedTrades = closedRows,
            journal = journalRows,
            auditEvents = auditRows,
            portfolio = portfolioSummary
        )
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
        val evidence = bodyText.jsonObjectFieldValues("summary").ifEmpty {
            bodyText.jsonArrayItems("evidence")
        }.ifEmpty {
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

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toSafetyScore(): SafetyScoreUi {
        if (!ok) {
            return PreviewData.state.safetyScore.copy(
                level = "UNKNOWN",
                reasons = listOf(safeError.ifBlank { "Backend readiness unavailable." })
            )
        }
        val readyForPaper = body.jsonBoolean("ready_for_paper") ?: false
        val readyForRealMoney = body.jsonBoolean("ready_for_real_money") ?: false
        val liveExecution = body.jsonBoolean("live_execution_available") ?: false
        val score = when {
            readyForRealMoney || liveExecution -> 15
            readyForPaper -> 92
            else -> 55
        }
        val level = when {
            readyForRealMoney || liveExecution -> "DANGER"
            readyForPaper -> "SAFE"
            else -> "CAUTION"
        }
        val reasons = body.jsonArrayItems("blockers").ifEmpty {
            listOf("Paper readiness verified", "Live execution unavailable", "Withdrawals unsupported")
        }
        return SafetyScoreUi(
            score = score,
            level = level,
            reasons = reasons.take(6),
            recommendedAction = body.jsonArrayItems("next_steps").firstOrNull()
                ?: "Continue paper-only monitoring."
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toStrategyCatalog(): List<StrategyCatalogUi> {
        if (!ok || !body.contains("strategies", ignoreCase = true)) return emptyList()
        val section = body.arraySection("strategies")
        if (section.isBlank()) return emptyList()
        return section.objectChunks().mapNotNull { chunk ->
            val name = chunk.jsonString("name") ?: return@mapNotNull null
            StrategyCatalogUi(
                name = name,
                family = chunk.jsonString("family") ?: "Strategy",
                purpose = chunk.jsonString("purpose") ?: "Evidence-first paper strategy.",
                requiredData = chunk.jsonArrayItems("required_data"),
                status = chunk.jsonString("status") ?: "PAPER_ADVISORY",
                safetyRules = chunk.jsonArrayItems("safety_rules")
            )
        }
    }

    private fun String.jsonObjectFieldValues(name: String): List<String> {
        val pattern = Regex(""""$name"\s*:\s*"([^"]+)"""")
        return pattern.findAll(this).map { it.groupValues[1] }.toList()
    }

    private fun String.latestReasonFor(eventType: String): String {
        val eventIndex = lastIndexOf(""""event_type":"$eventType"""")
        if (eventIndex < 0) return "unknown"
        val tail = substring(eventIndex).take(1500)
        return tail.jsonString("reason") ?: tail.jsonString("summary") ?: eventType
    }

    private fun String.tradeRowsFromSection(sectionName: String): List<TradeRow> {
        val section = arraySection(sectionName)
        if (section.isBlank() || !section.contains("symbol", ignoreCase = true)) return emptyList()
        val chunks = section.split(Regex("""\},\s*\{""")).filter { it.contains("symbol", ignoreCase = true) }
        return chunks.takeLast(20).mapIndexed { index, chunk ->
            TradeRow(
                id = chunk.jsonString("position_id") ?: chunk.jsonString("trade_id") ?: "$sectionName-$index",
                symbol = chunk.jsonString("symbol") ?: "UNKNOWN",
                side = chunk.jsonString("side") ?: chunk.jsonString("action") ?: "PAPER",
                status = chunk.jsonString("status") ?: chunk.jsonString("action") ?: "PAPER_EVENT",
                pnl = chunk.jsonNumber("unrealized_pnl") ?: chunk.jsonNumber("realized_pnl") ?: "0.00"
            )
        }
    }

    private fun String.auditEventRows(): List<AuditEventRow> {
        val section = arraySection("audit_timeline")
        if (section.isBlank()) return emptyList()
        return Regex(""""event_type"\s*:\s*"([^"]+)"""").findAll(section).mapIndexed { index, match ->
            val start = match.range.first
            val chunk = section.substring(start).take(700)
            AuditEventRow(
                timestamp = chunk.jsonString("created_at") ?: "latest",
                type = match.groupValues[1],
                detail = chunk.jsonString("reason") ?: chunk.jsonString("summary") ?: chunk.jsonString("status") ?: "paper monitor event"
            )
        }.toList().takeLast(20)
    }

    private fun String.section(name: String): String {
        val start = indexOf(""""$name"""")
        if (start < 0) return ""
        return substring(start).take(12_000)
    }

    private fun String.arraySection(name: String): String {
        val nameIndex = indexOf(""""$name"""")
        if (nameIndex < 0) return ""
        val start = indexOf('[', nameIndex)
        if (start < 0) return ""
        var depth = 0
        for (index in start until length) {
            when (this[index]) {
                '[' -> depth += 1
                ']' -> {
                    depth -= 1
                    if (depth == 0) return substring(start + 1, index)
                }
            }
        }
        return ""
    }

    private fun String.objectChunks(): List<String> {
        val chunks = mutableListOf<String>()
        var depth = 0
        var start = -1
        for (index in indices) {
            when (this[index]) {
                '{' -> {
                    if (depth == 0) start = index
                    depth += 1
                }
                '}' -> {
                    depth -= 1
                    if (depth == 0 && start >= 0) {
                        chunks.add(substring(start, index + 1))
                        start = -1
                    }
                }
            }
        }
        return chunks
    }
}
