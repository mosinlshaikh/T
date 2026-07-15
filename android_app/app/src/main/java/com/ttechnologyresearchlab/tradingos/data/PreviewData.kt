package com.ttechnologyresearchlab.tradingos.data

object PreviewData {
    val state = TradingOsUiState(
        reports = listOf(
            ReportSummary("Daily Report", "preview", "DEVELOPMENT PREVIEW DATA"),
            ReportSummary("Performance", "preview", "Paper-mode analytics only"),
            ReportSummary("Risk", "preview", "Risk engine remains active"),
            ReportSummary("Hallucination", "preview", "Unsupported claims are blocked")
        ),
        auditEvents = listOf(
            AuditEventRow("preview", "runtime_heartbeat", "DEVELOPMENT PREVIEW DATA"),
            AuditEventRow("preview", "api_readiness", "READY_FOR_PAPER")
        ),
        openTrades = listOf(
            TradeRow("preview-open", "BTCUSDT", "BUY", "PAPER_OPEN", "0.00")
        ),
        closedTrades = listOf(
            TradeRow("preview-closed", "ETHUSDT", "BUY", "PAPER_CLOSED", "0.00")
        ),
        journal = listOf(
            TradeRow("preview-fill", "BTCUSDT", "PAPER", "FILL_PREVIEW", "0.00")
        ),
        strategyCatalog = listOf(
            StrategyCatalogUi(
                "MULTI_TIMEFRAME_TREND_ALIGNMENT",
                "Candle / Structure",
                "DEVELOPMENT PREVIEW DATA: backend strategy catalog loads when connected.",
                listOf("candles_1m", "candles_5m", "candles_15m")
            ),
            StrategyCatalogUi(
                "ORDER_BOOK_IMBALANCE_SCALPER",
                "Order Book",
                "DEVELOPMENT PREVIEW DATA: spread, wall, and depth evidence required.",
                listOf("order_book_bids", "order_book_asks", "spread")
            ),
            StrategyCatalogUi(
                "MULTI_FACTOR_MASTER_COMBINER",
                "Composite",
                "DEVELOPMENT PREVIEW DATA: combines evidence only; no live execution.",
                listOf("candle_signal", "order_book_signal", "risk_result")
            )
        ),
        paperSession = PaperSessionUi(
            running = false,
            symbols = listOf("BTCUSDT", "ETHUSDT"),
            scanCount = 0,
            bestCandidate = "DEVELOPMENT PREVIEW DATA",
            bestAction = "HOLD",
            lastReason = "Backend paper session status loads when connected."
        ),
        dashboardCharts = DashboardChartsUi(
            holdCount = 3,
            lowConfidence = 3,
            averageConfidence = "0.43"
        ),
        decisionTimeline = listOf(
            TimelineEventUi(
                timestamp = "preview",
                type = "ai_decision",
                title = "SKIP BTCUSDT",
                detail = "DEVELOPMENT PREVIEW DATA: missing evidence means no paper trade.",
                status = "SKIP",
                symbol = "BTCUSDT"
            )
        ),
        tradeTimeline = listOf(
            TimelineEventUi(
                timestamp = "preview",
                type = "paper_trade",
                title = "No open paper trade",
                detail = "DEVELOPMENT PREVIEW DATA: backend paper journal loads when connected.",
                status = "PAPER_ONLY"
            )
        ),
        auditTimeline = listOf(
            TimelineEventUi(
                timestamp = "preview",
                type = "runtime_heartbeat",
                title = "Runtime Heartbeat",
                detail = "DEVELOPMENT PREVIEW DATA",
                status = "paper"
            )
        ),
        marketEvidenceFeed = listOf(
            MarketEvidenceUi(
                timestamp = "preview",
                layer = "Candle",
                signal = "unknown",
                confidence = "unknown",
                summary = "DEVELOPMENT PREVIEW DATA: backend market evidence loads when connected.",
                symbol = "BTCUSDT",
                source = "preview"
            )
        ),
        candleDetail = CandleDetailUi(
            candleCount = 0,
            trend = "unknown",
            latestClose = "DEVELOPMENT PREVIEW DATA",
            missingData = listOf("backend_connection", "candles"),
            decisionRule = "Missing candle data = SKIP"
        ),
        paperScanSummary = PaperScanSummaryUi(
            symbol = "BTCUSDT",
            action = "SKIP",
            status = "DEVELOPMENT PREVIEW DATA",
            reason = "Backend paper scan summary loads when connected.",
            whyNotTraded = "Preview only."
        ),
        paperDemoReadiness = PaperDemoReadinessUi(
            monitoringPercent = 0,
            demoPercent = 0,
            readyForPaperDemo = false,
            remaining = listOf("backend_connection")
        ),
        performanceWheel = PerformanceWheelUi(
            overallScore = 0,
            netPnl = "0.00",
            segments = listOf(
                PerformanceWheelSegmentUi("Candle Reading", 0, "DEVELOPMENT PREVIEW DATA"),
                PerformanceWheelSegmentUi("Whale Tracking", 0, "DEVELOPMENT PREVIEW DATA"),
                PerformanceWheelSegmentUi("News Risk", 0, "DEVELOPMENT PREVIEW DATA"),
                PerformanceWheelSegmentUi("Order Book", 0, "DEVELOPMENT PREVIEW DATA"),
                PerformanceWheelSegmentUi("Risk Engine", 100, "PAPER SAFE"),
                PerformanceWheelSegmentUi("Zero Hallucination", 100, "ACTIVE")
            )
        ),
        tradeQuality = TradeQualityUi(
            score = 0,
            level = "UNKNOWN",
            recommendedAction = "SKIP",
            tradeAllowed = false,
            reason = "DEVELOPMENT PREVIEW DATA: backend trade quality loads when connected.",
            missingData = listOf("backend_connection")
        ),
        noTradeZone = NoTradeZoneUi(
            active = true,
            zone = "NO_TRADE",
            recommendedAction = "SKIP",
            reasons = listOf("DEVELOPMENT PREVIEW DATA")
        ),
        strategyBlockers = StrategyBlockersUi(
            windowRows = 0,
            noTradeCount = 0,
            lowConfidenceCount = 0,
            topBlockers = listOf("DEVELOPMENT PREVIEW DATA"),
            recommendations = listOf("Connect backend to load real paper strategy blockers.")
        ),
        shadowMode = ShadowModeUi(
            enabled = true,
            mode = "PAPER_SHADOW_ONLY",
            wouldDo = "SKIP",
            reason = "DEVELOPMENT PREVIEW DATA: shadow-mode monitor loads when connected."
        ),
        coinUniverse = CoinUniverseUi(
            symbolCount = 0,
            scanBatchLimit = 40,
            symbolsPreview = listOf("DEVELOPMENT PREVIEW DATA"),
            rule = "Backend loads complete active Binance Spot USDT universe when connected."
        ),
        marketRadar = MarketRadarUi(
            candidates = listOf("DEVELOPMENT PREVIEW DATA"),
            deepScanSymbols = listOf("Connect backend for radar candidates."),
            rankingRule = "Preview only."
        ),
        dailyTarget = DailyTargetUi(
            targetPnlPct = "10",
            recommendedMode = "PAPER_DISCOVERY",
            rules = listOf("10% daily PnL is a target, not a promise.")
        ),
        offlineSync = OfflineSyncUi(
            status = "PREVIEW",
            cacheStatus = "DEVELOPMENT PREVIEW DATA"
        )
    )
}
