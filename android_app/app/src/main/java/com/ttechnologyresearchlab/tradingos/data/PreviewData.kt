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
        )
    )
}
