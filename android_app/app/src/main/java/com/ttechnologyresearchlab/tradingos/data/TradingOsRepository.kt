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
                val heartbeat = health.body.jsonString("last_heartbeat")
                    ?: health.body.jsonNumber("last_heartbeat_count")?.let { "Heartbeat count $it" }
                    ?: "No heartbeat yet"
                val latestDecisionResult = apiClient.getLatestDecision()
                val latestDecision = latestDecisionResult.toDecisionSummary()
                val openPositionsResult = apiClient.getOpenPositions()
                val openTrades = openPositionsResult.toTradeRows()
                val monitorResult = apiClient.getPaperLiveMonitor()
                val monitorState = monitorResult.toMonitorState()
                val readinessResult = apiClient.getRealWorldReadiness()
                val safetyScore = readinessResult.toSafetyScore()
                val statement = apiClient.getStatementReport().toStatement(
                    apiClient.getSevenDayStatementReport()
                )
                val derivatives = apiClient.getDerivativesReadiness().toDerivatives(
                    apiClient.getDerivativesRiskEstimate()
                )
                val strategyCatalog = apiClient.getStrategyCatalog().toStrategyCatalog()
                val paperSession = apiClient.getPaperSessionStatus().toPaperSession()
                val dashboardCharts = apiClient.getDashboardCharts().toDashboardCharts()
                val timelines = apiClient.getDashboardTimelines().toDashboardTimelines()
                val marketEvidenceFeed = apiClient.getMarketEvidenceFeed().toMarketEvidenceFeed()
                val candleDetail = apiClient.getCandleDetail().toCandleDetail()
                val candleStudies = apiClient.getCandleStudy().toCandleStudies()
                val paperScanSummary = apiClient.getPaperScanSummary().toPaperScanSummary()
                val paperScanHistory = apiClient.getPaperScanHistory().toPaperScanHistory()
                val watchlistCandidates = apiClient.getWatchlistCandidates().toWatchlistCandidates()
                val paperDemoReadiness = apiClient.getPaperDemoReadiness().toPaperDemoReadiness()
                val performanceWheel = apiClient.getPerformanceWheel().toPerformanceWheel()
                val tradeQuality = apiClient.getTradeQuality().toTradeQuality()
                val noTradeZone = apiClient.getNoTradeZone().toNoTradeZone()
                val strategyBlockers = apiClient.getStrategyBlockers().toStrategyBlockers()
                val shadowMode = apiClient.getShadowMode().toShadowMode()
                val coinUniverse = apiClient.getSymbolUniverse().toCoinUniverse()
                val fastMarketState = apiClient.getFastMarketState().toMarketRadar()
                val marketRadar = if (fastMarketState.cacheTickerCount > 0 || fastMarketState.candidates.isNotEmpty()) {
                    fastMarketState
                } else {
                    apiClient.getMarketRadar().toMarketRadar()
                }
                val dailyTarget = apiClient.getDailyTarget().toDailyTarget()
                PreviewData.state.copy(
                    isPreviewData = false,
                    connectionStatus = "Backend reachable",
                    backendConnectionState = BackendConnectionState.CONNECTED,
                    lastHeartbeat = heartbeat,
                    offlineSync = OfflineSyncUi(
                        status = "SYNCED",
                        lastSuccessfulSync = health.body.jsonString("timestamp") ?: "latest",
                        cacheStatus = "Fresh Railway backend data"
                    ),
                    lastKnownBotState = supervisorState,
                    latestDecision = monitorState.latestDecision ?: latestDecision,
                    marketIntelligence = monitorState.marketIntelligence,
                    openTrades = monitorState.openTrades.ifEmpty { openTrades },
                    closedTrades = monitorState.closedTrades,
                    journal = monitorState.journal,
                    auditEvents = monitorState.auditEvents,
                    portfolio = monitorState.portfolio ?: PreviewData.state.portfolio,
                    safetyScore = safetyScore,
                    statement = statement,
                    derivatives = derivatives,
                    strategyCatalog = strategyCatalog.ifEmpty { PreviewData.state.strategyCatalog },
                    paperSession = paperSession,
                    dashboardCharts = dashboardCharts,
                    decisionTimeline = timelines.decisionTimeline,
                    tradeTimeline = timelines.tradeTimeline,
                    auditTimeline = timelines.auditTimeline,
                    marketEvidenceFeed = marketEvidenceFeed,
                    candleDetail = candleDetail,
                    candleStudies = candleStudies,
                    paperScanSummary = paperScanSummary,
                    paperScanHistory = paperScanHistory,
                    watchlistCandidates = watchlistCandidates,
                    paperDemoReadiness = paperDemoReadiness,
                    performanceWheel = performanceWheel,
                    tradeQuality = tradeQuality,
                    noTradeZone = noTradeZone,
                    strategyBlockers = strategyBlockers,
                    shadowMode = shadowMode,
                    coinUniverse = coinUniverse,
                    marketRadar = marketRadar,
                    dailyTarget = dailyTarget,
                    botStatus = PreviewData.state.botStatus.copy(
                        botState = supervisorState,
                        liveTradingEnabled = liveTradingEnabled
                    ),
                    shutdownState = shutdownState
                )
            } else {
                PreviewData.state.copy(
                    connectionStatus = health.safeError,
                    backendConnectionState = BackendConnectionState.DISCONNECTED,
                    offlineSync = OfflineSyncUi(
                        status = "OFFLINE",
                        cacheStatus = "DEVELOPMENT PREVIEW DATA"
                    )
                )
            }
        } catch (_: Exception) {
            PreviewData.state.copy(
                connectionStatus = "DEVELOPMENT PREVIEW DATA",
                backendConnectionState = BackendConnectionState.DISCONNECTED,
                offlineSync = OfflineSyncUi(
                    status = "OFFLINE",
                    cacheStatus = "DEVELOPMENT PREVIEW DATA"
                )
            )
        }
    }

    suspend fun startBot() = runCatching { apiClient.startBot() }
    suspend fun gracefulStop() = runCatching { apiClient.stopGraceful() }
    suspend fun emergencyStop() = runCatching { apiClient.emergencyStop() }
    suspend fun pauseNewTrades() = runCatching { apiClient.pauseNewTrades() }
    suspend fun resumePaperTrades() = runCatching { apiClient.resumePaperTrades() }
    suspend fun runLiveMarketPaperDemo() = runCatching { apiClient.runLiveMarketPaperDemo() }
    suspend fun openManualPaperDemo() = runCatching { apiClient.openManualPaperDemo() }
    suspend fun closeManualPaperDemo() = runCatching { apiClient.closeManualPaperDemo() }
    suspend fun simulateManualStopLoss() = runCatching { apiClient.simulateManualStopLoss() }
    suspend fun simulateManualTakeProfit() = runCatching { apiClient.simulateManualTakeProfit() }
    suspend fun startPaperSession() = runCatching { apiClient.startPaperSession() }
    suspend fun stopPaperSession() = runCatching { apiClient.stopPaperSession() }
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

    private data class DashboardTimelines(
        val decisionTimeline: List<TimelineEventUi> = PreviewData.state.decisionTimeline,
        val tradeTimeline: List<TimelineEventUi> = PreviewData.state.tradeTimeline,
        val auditTimeline: List<TimelineEventUi> = PreviewData.state.auditTimeline
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

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toStatement(
        sevenDayResult: com.ttechnologyresearchlab.tradingos.network.ApiClientResult
    ): StatementUi {
        if (!ok) return PreviewData.state.statement
        val safetyChecks = body.arraySection("safety_checks").objectChunks().map { chunk ->
            "${chunk.jsonString("name") ?: "Safety check"}: ${chunk.jsonBoolean("passed") ?: false}"
        }
        val tradeRows = body.arraySection("trade_rows").objectChunks().map { chunk ->
            val symbol = chunk.jsonString("symbol") ?: "UNKNOWN"
            val status = chunk.jsonString("status") ?: "PAPER"
            val pnl = chunk.jsonNumber("realized_pnl") ?: "0.00"
            "$symbol $status PnL=$pnl"
        }
        val paperScanRows = body.arraySection("paper_scan_rows").objectChunks().map { chunk ->
            val symbol = chunk.jsonString("symbol") ?: "UNKNOWN"
            val action = chunk.jsonString("action") ?: "SKIP"
            val confidence = chunk.jsonNumber("confidence") ?: "0.00"
            val why = chunk.jsonString("why_not_traded") ?: "No paper trade was opened by policy."
            "$symbol $action confidence=$confidence | $why"
        }
        return StatementUi(
            statementId = body.jsonString("statement_id") ?: "paper-statement",
            windowHours = body.jsonNumber("window_hours") ?: "18",
            realizedPnl = body.jsonNumber("realized_pnl") ?: "0.00",
            unrealizedPnl = body.jsonNumber("unrealized_pnl") ?: "0.00",
            netPnl = body.jsonNumber("net_pnl") ?: "0.00",
            grossProfit = body.jsonNumber("gross_profit") ?: "0.00",
            grossLoss = body.jsonNumber("gross_loss") ?: "0.00",
            winRatePct = body.jsonNumber("win_rate_pct") ?: "0.00",
            openPositions = body.jsonNumber("open_positions") ?: "0",
            closedPositions = body.jsonNumber("closed_positions") ?: "0",
            journalEntries = body.jsonNumber("journal_entries") ?: "0",
            safetyChecks = safetyChecks,
            tradeRows = tradeRows.takeLast(12),
            paperScanRows = paperScanRows.takeLast(12),
            notes = body.jsonArrayItems("notes"),
            sevenDayNetPnl = sevenDayResult.body.jsonNumber("net_pnl") ?: "0.00",
            sevenDayRealizedPnl = sevenDayResult.body.jsonNumber("realized_pnl") ?: "0.00",
            sevenDayClosedPositions = sevenDayResult.body.jsonNumber("closed_positions") ?: "0",
            sevenDayWinRatePct = sevenDayResult.body.jsonNumber("win_rate_pct") ?: "0.00"
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toDerivatives(
        riskEstimate: com.ttechnologyresearchlab.tradingos.network.ApiClientResult
    ): DerivativesUi {
        val readinessBody = if (ok) body else ""
        val riskBody = if (riskEstimate.ok) riskEstimate.body else ""
        return DerivativesUi(
            mode = readinessBody.jsonString("mode") ?: "RESEARCH_ONLY",
            futuresExecutionAvailable = readinessBody.jsonBoolean("futures_execution_available") ?: false,
            optionsExecutionAvailable = readinessBody.jsonBoolean("options_execution_available") ?: false,
            leverageExecutionAvailable = readinessBody.jsonBoolean("leverage_execution_available") ?: false,
            notionalUsdt = riskBody.jsonNumber("notional_usdt") ?: "100",
            leverage = riskBody.jsonNumber("leverage") ?: "2",
            marginEstimateUsdt = riskBody.jsonNumber("margin_estimate_usdt") ?: "50",
            estimatedLossUsdt = riskBody.jsonNumber("estimated_loss_usdt") ?: "1",
            liquidationWarning = riskBody.jsonString("liquidation_warning") ?: "Paper-only risk estimate.",
            blockedReasons = readinessBody.jsonArrayItems("blocked_reasons"),
            allowedFeatures = readinessBody.jsonArrayItems("allowed_features"),
            safetyNotes = riskBody.jsonArrayItems("safety_notes")
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toPaperSession(): PaperSessionUi {
        if (!ok) return PreviewData.state.paperSession
        val best = body.section("best_candidate")
        return PaperSessionUi(
            running = body.jsonBoolean("running") ?: false,
            sessionId = body.jsonString("session_id") ?: "",
            startedAt = body.jsonString("started_at") ?: "",
            symbols = body.jsonArrayItems("symbols"),
            timeframe = body.jsonString("timeframe") ?: "5m",
            intervalSeconds = body.jsonNumber("interval_seconds") ?: "300",
            scanCount = body.jsonNumber("scan_count")?.toIntOrNull() ?: 0,
            bestCandidate = best.jsonString("symbol") ?: "unknown",
            bestAction = best.jsonString("action") ?: "unknown",
            bestConfidence = best.jsonNumber("confidence") ?: "0.00",
            lastReason = best.jsonString("reason") ?: body.jsonString("last_error") ?: "No paper session scan yet.",
            autoResumeEnabled = body.jsonBoolean("auto_resume_enabled") ?: false,
            desiredSymbols = body.jsonArrayItems("desired_symbols"),
            publicDataOnly = body.jsonBoolean("public_data_only") ?: true,
            liveTradingEnabled = body.jsonBoolean("live_trading_enabled") ?: false
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toDashboardCharts(): DashboardChartsUi {
        if (!ok) return PreviewData.state.dashboardCharts
        return DashboardChartsUi(
            buyCount = body.jsonNumber("BUY")?.toIntOrNull() ?: 0,
            sellCount = body.jsonNumber("SELL")?.toIntOrNull() ?: 0,
            holdCount = body.jsonNumber("HOLD")?.toIntOrNull() ?: 0,
            skipCount = body.jsonNumber("SKIP")?.toIntOrNull() ?: 0,
            highConfidence = body.jsonNumber("high")?.toIntOrNull() ?: 0,
            mediumConfidence = body.jsonNumber("medium")?.toIntOrNull() ?: 0,
            lowConfidence = body.jsonNumber("low")?.toIntOrNull() ?: 0,
            averageConfidence = body.jsonNumber("average") ?: "0.00"
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toDashboardTimelines(): DashboardTimelines {
        if (!ok) return DashboardTimelines()
        return DashboardTimelines(
            decisionTimeline = body.timelineRowsFromSection("decision_timeline").ifEmpty { PreviewData.state.decisionTimeline },
            tradeTimeline = body.timelineRowsFromSection("trade_timeline").ifEmpty { PreviewData.state.tradeTimeline },
            auditTimeline = body.timelineRowsFromSection("audit_timeline").ifEmpty { PreviewData.state.auditTimeline }
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toMarketEvidenceFeed(): List<MarketEvidenceUi> {
        if (!ok) return PreviewData.state.marketEvidenceFeed
        val section = body.arraySection("items")
        if (section.isBlank()) return PreviewData.state.marketEvidenceFeed
        return section.objectChunks().map { chunk ->
            MarketEvidenceUi(
                timestamp = chunk.jsonString("timestamp") ?: "unknown",
                layer = chunk.jsonString("layer") ?: "unknown",
                signal = chunk.jsonString("signal") ?: "unknown",
                confidence = chunk.jsonNumber("confidence") ?: chunk.jsonString("confidence") ?: "unknown",
                summary = chunk.jsonString("summary") ?: "unknown / insufficient data",
                symbol = chunk.jsonString("symbol") ?: "",
                source = chunk.jsonString("source") ?: "unknown",
                missingData = chunk.jsonArrayItems("missing_data"),
                conflicts = chunk.jsonArrayItems("conflicts")
            )
        }.takeLast(20).ifEmpty { PreviewData.state.marketEvidenceFeed }
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toCandleDetail(): CandleDetailUi {
        if (!ok) return PreviewData.state.candleDetail
        val candlesSection = body.arraySection("candles")
        val closeValues = Regex(""""close"\s*:\s*(-?\d+(?:\.\d+)?)""")
            .findAll(candlesSection)
            .map { it.groupValues[1] }
            .toList()
            .takeLast(12)
        return CandleDetailUi(
            symbol = body.jsonString("symbol") ?: "BTCUSDT",
            timeframe = body.jsonString("timeframe") ?: "5m",
            candleCount = closeValues.size,
            trend = body.jsonString("trend") ?: "unknown",
            latestClose = body.jsonNumber("latest_close") ?: body.jsonString("latest_close") ?: "unknown",
            rangeHigh = body.jsonNumber("range_high") ?: body.jsonString("range_high") ?: "unknown",
            rangeLow = body.jsonNumber("range_low") ?: body.jsonString("range_low") ?: "unknown",
            volumeTotal = body.jsonNumber("volume_total") ?: "0.00",
            source = body.jsonString("source") ?: "unknown",
            missingData = body.jsonArrayItems("missing_data"),
            decisionRule = body.jsonString("decision_rule") ?: "Missing candle data = SKIP",
            sparklineCloses = closeValues
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toCandleStudies(): List<CandleStudyUi> {
        if (!ok) return PreviewData.state.candleStudies
        val section = body.arraySection("studies")
        if (section.isBlank()) return PreviewData.state.candleStudies
        return section.objectChunks().map { chunk ->
            CandleStudyUi(
                timeframe = chunk.jsonString("timeframe") ?: "unknown",
                trend = chunk.jsonString("trend") ?: "unknown",
                confidence = chunk.jsonNumber("confidence_score") ?: "0.00",
                moveReason = chunk.jsonString("move_reason") ?: "Candle study unavailable.",
                learningNotes = chunk.jsonArrayItems("learning_notes"),
                missingData = chunk.jsonArrayItems("missing_data")
            )
        }.ifEmpty { PreviewData.state.candleStudies }
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toPaperScanSummary(): PaperScanSummaryUi {
        if (!ok) return PreviewData.state.paperScanSummary
        return PaperScanSummaryUi(
            symbol = body.jsonString("latest_symbol") ?: "unknown",
            timeframe = body.jsonString("latest_timeframe") ?: "unknown",
            action = body.jsonString("latest_action") ?: "unknown",
            status = body.jsonString("latest_status") ?: "unknown",
            confidence = body.jsonNumber("latest_confidence") ?: "0.00",
            reason = body.jsonString("latest_reason") ?: "No paper scan result available.",
            whyNotTraded = body.jsonString("why_not_traded") ?: "No paper trade was opened by policy.",
            timestamp = body.jsonString("latest_timestamp") ?: "unknown",
            runCount = body.jsonNumber("run_count")?.toIntOrNull() ?: 0,
            tradeAllowed = body.jsonBoolean("trade_allowed") ?: false,
            selectionMode = body.jsonString("latest_scan_selection_mode") ?: "unknown",
            selectionSource = body.jsonString("latest_scan_selection_source") ?: "unknown",
            scanSymbolCount = body.jsonNumber("latest_scan_symbol_count")?.toIntOrNull() ?: 0,
            scanResultCount = body.jsonNumber("latest_scan_result_count")?.toIntOrNull() ?: 0,
            scanErrorCount = body.jsonNumber("latest_scan_error_count")?.toIntOrNull() ?: 0,
            paperTradeBlocker = body.jsonString("paper_trade_blocker") ?: "unknown",
            profitTargetNote = body.jsonString("profit_target_note")
                ?: "1% daily PnL target is a target, not guaranteed."
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toPaperScanHistory(): List<PaperScanHistoryRowUi> {
        if (!ok) return PreviewData.state.paperScanHistory
        val section = body.arraySection("rows")
        if (section.isBlank()) return emptyList()
        return section.paperScanRows().takeLast(20)
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toWatchlistCandidates(): List<PaperScanHistoryRowUi> {
        if (!ok) return PreviewData.state.watchlistCandidates
        val section = body.arraySection("candidates")
        if (section.isBlank()) return emptyList()
        return section.paperScanRows().take(10)
    }

    private fun String.paperScanRows(): List<PaperScanHistoryRowUi> {
        return objectChunks().map { chunk ->
            PaperScanHistoryRowUi(
                timestamp = chunk.jsonString("timestamp") ?: "unknown",
                symbol = chunk.jsonString("symbol") ?: "UNKNOWN",
                timeframe = chunk.jsonString("timeframe") ?: "",
                action = chunk.jsonString("action") ?: "SKIP",
                status = chunk.jsonString("status") ?: "SKIP",
                confidence = chunk.jsonNumber("confidence") ?: "0.00",
                tradeAllowed = chunk.jsonBoolean("trade_allowed") ?: false,
                whyNotTraded = chunk.jsonString("why_not_traded") ?: "No paper trade was opened by policy.",
                strategyBreakdown = chunk.strategyBreakdownRows(),
                pipelineStages = chunk.pipelineStageRows(),
                source = chunk.jsonString("source") ?: "paper_scan"
            )
        }
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toPaperDemoReadiness(): PaperDemoReadinessUi {
        if (!ok) return PreviewData.state.paperDemoReadiness
        return PaperDemoReadinessUi(
            monitoringPercent = body.jsonNumber("paper_backend_apk_monitoring_percent")?.toIntOrNull() ?: 0,
            demoPercent = body.jsonNumber("paper_demo_readiness_percent")?.toIntOrNull() ?: 0,
            readyForPaperDemo = body.jsonBoolean("ready_for_paper_demo") ?: false,
            remaining = body.jsonObjectFieldValues("name").takeLast(8)
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toPerformanceWheel(): PerformanceWheelUi {
        if (!ok) return PreviewData.state.performanceWheel
        val segments = body.arraySection("segments").objectChunks().map { chunk ->
            PerformanceWheelSegmentUi(
                name = chunk.jsonString("name") ?: "unknown",
                score = chunk.jsonNumber("score")?.toIntOrNull() ?: 0,
                status = chunk.jsonString("status") ?: "UNKNOWN"
            )
        }
        return PerformanceWheelUi(
            overallScore = body.jsonNumber("overall_score")?.toIntOrNull() ?: 0,
            segments = segments,
            netPnl = body.jsonNumber("net_pnl") ?: "0.00"
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toTradeQuality(): TradeQualityUi {
        if (!ok) return PreviewData.state.tradeQuality
        return TradeQualityUi(
            score = body.jsonNumber("score")?.toIntOrNull() ?: 0,
            level = body.jsonString("level") ?: "UNKNOWN",
            recommendedAction = body.jsonString("recommended_action") ?: "SKIP",
            tradeAllowed = body.jsonBoolean("trade_allowed") ?: false,
            reason = body.jsonString("reason") ?: "Trade quality unavailable.",
            latestSymbol = body.jsonString("latest_symbol") ?: "unknown",
            latestTimestamp = body.jsonString("latest_timestamp") ?: "unknown",
            evidenceSymbolAligned = body.jsonBoolean("evidence_symbol_aligned") ?: false,
            warnings = body.jsonArrayItems("warnings"),
            missingData = body.jsonArrayItems("missing_data"),
            conflicts = body.jsonArrayItems("conflicts")
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toNoTradeZone(): NoTradeZoneUi {
        if (!ok) return PreviewData.state.noTradeZone
        return NoTradeZoneUi(
            active = body.jsonBoolean("active") ?: true,
            zone = body.jsonString("zone") ?: "NO_TRADE",
            recommendedAction = body.jsonString("recommended_action") ?: "SKIP",
            reasons = body.jsonArrayItems("reasons")
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toStrategyBlockers(): StrategyBlockersUi {
        if (!ok) return PreviewData.state.strategyBlockers
        val actions = body.section("action_counts")
        val buy = actions.jsonNumber("BUY") ?: "0"
        val sell = actions.jsonNumber("SELL") ?: "0"
        val hold = actions.jsonNumber("HOLD") ?: "0"
        val skip = actions.jsonNumber("SKIP") ?: "0"
        val topBlockers = body.arraySection("top_blockers").objectChunks().map { chunk ->
            "${chunk.jsonString("blocker") ?: "blocker"} = ${chunk.jsonNumber("count") ?: "0"}"
        }.take(8)
        val topSymbols = body.arraySection("top_symbols").objectChunks().map { chunk ->
            "${chunk.jsonString("symbol") ?: "UNKNOWN"} = ${chunk.jsonNumber("count") ?: "0"}"
        }.take(10)
        val examples = body.arraySection("examples").objectChunks().map { chunk ->
            val symbol = chunk.jsonString("symbol") ?: "UNKNOWN"
            val action = chunk.jsonString("action") ?: "SKIP"
            val confidence = chunk.jsonNumber("confidence") ?: "0.00"
            val why = chunk.jsonString("why_not_traded") ?: "No trade opened."
            "$symbol $action confidence=$confidence - $why"
        }.take(8)
        return StrategyBlockersUi(
            windowRows = body.jsonNumber("window_rows")?.toIntOrNull() ?: 0,
            noTradeCount = body.jsonNumber("no_trade_count")?.toIntOrNull() ?: 0,
            lowConfidenceCount = body.jsonNumber("low_confidence_count")?.toIntOrNull() ?: 0,
            actionCounts = "BUY $buy / SELL $sell / HOLD $hold / SKIP $skip",
            topBlockers = topBlockers,
            topSymbols = topSymbols,
            examples = examples,
            recommendations = body.jsonArrayItems("recommendations"),
            tuningPolicy = body.jsonString("tuning_policy") ?: "Advisory only. Live trading remains disabled."
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toShadowMode(): ShadowModeUi {
        if (!ok) return PreviewData.state.shadowMode
        return ShadowModeUi(
            enabled = body.jsonBoolean("enabled") ?: true,
            mode = body.jsonString("mode") ?: "PAPER_SHADOW_ONLY",
            wouldDo = body.jsonString("would_do") ?: "SKIP",
            reason = body.jsonString("reason") ?: "Shadow mode unavailable.",
            noTradeZoneActive = body.jsonBoolean("no_trade_zone_active") ?: true
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toCoinUniverse(): CoinUniverseUi {
        if (!ok) return PreviewData.state.coinUniverse
        return CoinUniverseUi(
            mode = body.jsonString("mode") ?: "ALL_ACTIVE_USDT_SPOT",
            symbolCount = body.jsonNumber("symbol_count")?.toIntOrNull() ?: 0,
            scanBatchLimit = body.jsonNumber("scan_batch_limit")?.toIntOrNull() ?: 0,
            symbolsPreview = body.jsonArrayItems("symbols_preview"),
            rule = body.jsonString("rule") ?: "Know full active Spot USDT universe; scan in safe batches."
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toMarketRadar(): MarketRadarUi {
        if (!ok) return PreviewData.state.marketRadar
        val candidates = body.arraySection("candidates").objectChunks().map { chunk ->
            val symbol = chunk.jsonString("symbol") ?: "UNKNOWN"
            val score = chunk.jsonNumber("radar_score") ?: "0"
            val move = chunk.jsonNumber("price_change_pct") ?: "0"
            val volume = chunk.jsonNumber("quote_volume") ?: "0"
            "$symbol score=$score move=$move% volume=$volume"
        }.take(12)
        val cacheReady = body.jsonBoolean("stream_cache_ready") ?: false
        val tickerCount = body.jsonNumber("ticker_count")?.toIntOrNull()
            ?: body.jsonNumber("symbols_seen")?.toIntOrNull()
            ?: 0
        return MarketRadarUi(
            mode = body.jsonString("mode") ?: "PUBLIC_MARKET_RADAR",
            symbolsSeen = body.jsonNumber("symbols_seen")?.toIntOrNull() ?: tickerCount,
            cacheReady = cacheReady,
            cacheTickerCount = tickerCount,
            cacheAgeSeconds = body.jsonNumber("last_update_age_seconds") ?: "unknown",
            streamConnected = body.jsonBoolean("connected") ?: false,
            seededFromRest = body.jsonBoolean("seeded_from_rest") ?: false,
            candidates = candidates,
            deepScanSymbols = body.jsonArrayItems("deep_scan_symbols"),
            rankingRule = body.jsonString("ranking_rule") ?: "volume + move + volatility + activity",
            latencyDesign = body.jsonString("latency_design") ?: "",
            error = body.jsonString("error") ?: "",
            rule = body.jsonString("rule") ?: "Public-data radar only."
        )
    }

    private fun com.ttechnologyresearchlab.tradingos.network.ApiClientResult.toDailyTarget(): DailyTargetUi {
        if (!ok) return PreviewData.state.dailyTarget
        return DailyTargetUi(
            targetPnlPct = body.jsonNumber("target_pnl_pct") ?: "10",
            targetAmountUsdt = body.jsonNumber("target_amount_usdt") ?: "0.00",
            currentDailyPnlUsdt = body.jsonNumber("current_daily_pnl_usdt") ?: "0.00",
            progressPct = body.jsonNumber("progress_pct") ?: "0.00",
            targetReached = body.jsonBoolean("target_reached") ?: false,
            recommendedMode = body.jsonString("recommended_mode") ?: "PAPER_DISCOVERY",
            rules = body.jsonArrayItems("rules")
        )
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

    private fun String.timelineRowsFromSection(sectionName: String): List<TimelineEventUi> {
        val section = arraySection(sectionName)
        if (section.isBlank()) return emptyList()
        return section.objectChunks().map { chunk ->
            TimelineEventUi(
                timestamp = chunk.jsonString("timestamp") ?: "unknown",
                type = chunk.jsonString("event_type") ?: chunk.jsonString("type") ?: "paper_event",
                title = chunk.jsonString("title") ?: "paper event",
                detail = chunk.jsonString("detail") ?: "unknown / insufficient data",
                status = chunk.jsonString("status") ?: "paper",
                symbol = chunk.jsonString("symbol") ?: ""
            )
        }.takeLast(20)
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

    private fun String.strategyBreakdownRows(): List<String> {
        val section = arraySection("strategy_breakdown")
        if (section.isBlank()) return emptyList()
        return section.objectChunks().map { chunk ->
            val strategy = chunk.jsonString("strategy") ?: "strategy"
            val direction = chunk.jsonString("direction") ?: "unknown"
            val confidence = chunk.jsonNumber("confidence") ?: chunk.jsonString("confidence") ?: "unknown"
            "$strategy: $direction confidence=$confidence"
        }.takeLast(8)
    }

    private fun String.pipelineStageRows(): List<String> {
        val section = arraySection("pipeline_stages")
        if (section.isBlank()) return emptyList()
        return section.objectChunks().map { chunk ->
            val stage = chunk.jsonString("stage") ?: "stage"
            val outcome = chunk.jsonString("outcome") ?: "UNKNOWN"
            val reason = chunk.jsonString("reason_code") ?: "UNKNOWN"
            "$stage: $outcome / $reason"
        }.takeLast(10)
    }
}
