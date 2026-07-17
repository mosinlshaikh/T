package com.ttechnologyresearchlab.tradingos.data

import android.content.Context
import com.ttechnologyresearchlab.tradingos.localization.AppLanguage

class LocalDashboardCache(context: Context) {
    private val prefs = context.getSharedPreferences("ttrl_dashboard_cache", Context.MODE_PRIVATE)

    fun saveUiPreferences(state: TradingOsUiState) {
        prefs.edit()
            .putBoolean("onboarding_complete", state.onboardingComplete)
            .putBoolean("app_locked", state.appLocked)
            .putString("language", state.language.name)
            .putString("backend_base_url", state.backendBaseUrl)
            .apply()
    }

    fun save(state: TradingOsUiState) {
        if (state.isPreviewData) return
        prefs.edit()
            .putBoolean("onboarding_complete", state.onboardingComplete)
            .putBoolean("app_locked", state.appLocked)
            .putString("language", state.language.name)
            .putString("backend_base_url", state.backendBaseUrl)
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
        val language = runCatching {
            AppLanguage.valueOf(prefs.getString("language", base.language.name) ?: base.language.name)
        }.getOrDefault(base.language)
        val uiPrefs = base.copy(
            onboardingComplete = prefs.getBoolean("onboarding_complete", base.onboardingComplete),
            appLocked = prefs.getBoolean("app_locked", base.appLocked),
            language = language,
            backendBaseUrl = prefs.getString("backend_base_url", base.backendBaseUrl) ?: base.backendBaseUrl
        )
        val statementId = prefs.getString("statement_id", null) ?: return uiPrefs
        return uiPrefs.copy(
            isPreviewData = false,
            connectionStatus = "Offline cache loaded",
            backendConnectionState = BackendConnectionState.UNKNOWN,
            statement = uiPrefs.statement.copy(
                statementId = statementId,
                netPnl = prefs.getString("statement_net_pnl", "0.00") ?: "0.00",
                realizedPnl = prefs.getString("statement_realized_pnl", "0.00") ?: "0.00",
                unrealizedPnl = prefs.getString("statement_unrealized_pnl", "0.00") ?: "0.00",
                sevenDayNetPnl = prefs.getString("statement_7d_net_pnl", "0.00") ?: "0.00"
            ),
            portfolio = uiPrefs.portfolio.copy(
                paperBalanceUsdt = prefs.getString("portfolio_balance", uiPrefs.portfolio.paperBalanceUsdt)
                    ?: uiPrefs.portfolio.paperBalanceUsdt,
                dailyPnl = prefs.getString("portfolio_daily_pnl", "0.00") ?: "0.00"
            ),
            latestDecision = uiPrefs.latestDecision.copy(
                action = prefs.getString("latest_decision_action", "SKIP") ?: "SKIP",
                reason = prefs.getString("latest_decision_reason", "Cached decision unavailable.") ?: "Cached decision unavailable."
            ),
            performanceWheel = uiPrefs.performanceWheel.copy(
                overallScore = prefs.getInt("performance_overall", 0),
                netPnl = prefs.getString("performance_net_pnl", "0.00") ?: "0.00"
            ),
            tradeQuality = uiPrefs.tradeQuality.copy(
                score = prefs.getInt("trade_quality_score", 0),
                level = prefs.getString("trade_quality_level", "UNKNOWN") ?: "UNKNOWN"
            ),
            noTradeZone = uiPrefs.noTradeZone.copy(
                active = prefs.getBoolean("no_trade_zone_active", true),
                zone = prefs.getString("no_trade_zone", "NO_TRADE") ?: "NO_TRADE"
            ),
            shadowMode = uiPrefs.shadowMode.copy(
                wouldDo = prefs.getString("shadow_would_do", "SKIP") ?: "SKIP"
            ),
            coinUniverse = uiPrefs.coinUniverse.copy(
                symbolCount = prefs.getInt("coin_universe_count", 0),
                scanBatchLimit = prefs.getInt("coin_scan_batch_limit", 40)
            ),
            dailyTarget = uiPrefs.dailyTarget.copy(
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
