package com.ttechnologyresearchlab.tradingos.data

import android.content.Context

class LocalDashboardCache(context: Context) {
    private val prefs = context.getSharedPreferences("ttrl_dashboard_cache", Context.MODE_PRIVATE)

    fun save(state: TradingOsUiState) {
        if (state.isPreviewData) return
        prefs.edit()
            .putString("statement_id", state.statement.statementId)
            .putString("statement_net_pnl", state.statement.netPnl)
            .putString("statement_realized_pnl", state.statement.realizedPnl)
            .putString("statement_unrealized_pnl", state.statement.unrealizedPnl)
            .putString("statement_7d_net_pnl", state.statement.sevenDayNetPnl)
            .putString("portfolio_balance", state.portfolio.paperBalanceUsdt)
            .putString("portfolio_daily_pnl", state.portfolio.dailyPnl)
            .putString("latest_decision_action", state.latestDecision.action)
            .putString("latest_decision_reason", state.latestDecision.reason)
            .putInt("performance_overall", state.performanceWheel.overallScore)
            .putString("performance_net_pnl", state.performanceWheel.netPnl)
            .putInt("trade_quality_score", state.tradeQuality.score)
            .putString("trade_quality_level", state.tradeQuality.level)
            .putBoolean("no_trade_zone_active", state.noTradeZone.active)
            .putString("no_trade_zone", state.noTradeZone.zone)
            .putString("shadow_would_do", state.shadowMode.wouldDo)
            .putInt("coin_universe_count", state.coinUniverse.symbolCount)
            .putInt("coin_scan_batch_limit", state.coinUniverse.scanBatchLimit)
            .putString("daily_target_pct", state.dailyTarget.targetPnlPct)
            .putString("daily_target_amount", state.dailyTarget.targetAmountUsdt)
            .putString("daily_target_progress", state.dailyTarget.progressPct)
            .putString("daily_target_mode", state.dailyTarget.recommendedMode)
            .putString("last_successful_sync", state.offlineSync.lastSuccessfulSync)
            .apply()
    }

    fun load(base: TradingOsUiState = PreviewData.state): TradingOsUiState {
        val statementId = prefs.getString("statement_id", null) ?: return base
        return base.copy(
            isPreviewData = false,
            connectionStatus = "Offline cache loaded",
            backendConnectionState = BackendConnectionState.UNKNOWN,
            statement = base.statement.copy(
                statementId = statementId,
                netPnl = prefs.getString("statement_net_pnl", "0.00") ?: "0.00",
                realizedPnl = prefs.getString("statement_realized_pnl", "0.00") ?: "0.00",
                unrealizedPnl = prefs.getString("statement_unrealized_pnl", "0.00") ?: "0.00",
                sevenDayNetPnl = prefs.getString("statement_7d_net_pnl", "0.00") ?: "0.00"
            ),
            portfolio = base.portfolio.copy(
                paperBalanceUsdt = prefs.getString("portfolio_balance", base.portfolio.paperBalanceUsdt)
                    ?: base.portfolio.paperBalanceUsdt,
                dailyPnl = prefs.getString("portfolio_daily_pnl", "0.00") ?: "0.00"
            ),
            latestDecision = base.latestDecision.copy(
                action = prefs.getString("latest_decision_action", "SKIP") ?: "SKIP",
                reason = prefs.getString("latest_decision_reason", "Cached decision unavailable.") ?: "Cached decision unavailable."
            ),
            performanceWheel = base.performanceWheel.copy(
                overallScore = prefs.getInt("performance_overall", 0),
                netPnl = prefs.getString("performance_net_pnl", "0.00") ?: "0.00"
            ),
            tradeQuality = base.tradeQuality.copy(
                score = prefs.getInt("trade_quality_score", 0),
                level = prefs.getString("trade_quality_level", "UNKNOWN") ?: "UNKNOWN"
            ),
            noTradeZone = base.noTradeZone.copy(
                active = prefs.getBoolean("no_trade_zone_active", true),
                zone = prefs.getString("no_trade_zone", "NO_TRADE") ?: "NO_TRADE"
            ),
            shadowMode = base.shadowMode.copy(
                wouldDo = prefs.getString("shadow_would_do", "SKIP") ?: "SKIP"
            ),
            coinUniverse = base.coinUniverse.copy(
                symbolCount = prefs.getInt("coin_universe_count", 0),
                scanBatchLimit = prefs.getInt("coin_scan_batch_limit", 40)
            ),
            dailyTarget = base.dailyTarget.copy(
                targetPnlPct = prefs.getString("daily_target_pct", "10") ?: "10",
                targetAmountUsdt = prefs.getString("daily_target_amount", "0.00") ?: "0.00",
                progressPct = prefs.getString("daily_target_progress", "0.00") ?: "0.00",
                recommendedMode = prefs.getString("daily_target_mode", "PAPER_DISCOVERY") ?: "PAPER_DISCOVERY"
            ),
            offlineSync = OfflineSyncUi(
                status = "LOCAL_CACHE",
                lastSuccessfulSync = prefs.getString("last_successful_sync", "unknown") ?: "unknown",
                cacheStatus = "Stored phone cache shown; reconnect will refresh from backend."
            )
        )
    }
}
