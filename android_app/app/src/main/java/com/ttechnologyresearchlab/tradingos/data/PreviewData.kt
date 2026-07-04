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
        )
    )
}
