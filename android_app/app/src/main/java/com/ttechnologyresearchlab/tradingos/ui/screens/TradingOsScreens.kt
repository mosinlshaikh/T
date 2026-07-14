package com.ttechnologyresearchlab.tradingos.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Assessment
import androidx.compose.material.icons.outlined.Dashboard
import androidx.compose.material.icons.outlined.HealthAndSafety
import androidx.compose.material.icons.outlined.History
import androidx.compose.material.icons.outlined.Lock
import androidx.compose.material.icons.outlined.Menu
import androidx.compose.material.icons.outlined.Memory
import androidx.compose.material.icons.outlined.PieChart
import androidx.compose.material.icons.outlined.PowerSettingsNew
import androidx.compose.material.icons.outlined.Psychology
import androidx.compose.material.icons.outlined.RocketLaunch
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.Timeline
import androidx.compose.material.icons.outlined.Tune
import androidx.compose.material.icons.outlined.VpnKey
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.sp
import androidx.compose.ui.unit.dp
import com.ttechnologyresearchlab.tradingos.R
import com.ttechnologyresearchlab.tradingos.data.BackendConnectionState
import com.ttechnologyresearchlab.tradingos.data.CandleDetailUi
import com.ttechnologyresearchlab.tradingos.data.CandleStudyUi
import com.ttechnologyresearchlab.tradingos.data.MarketEvidenceUi
import com.ttechnologyresearchlab.tradingos.data.TimelineEventUi
import com.ttechnologyresearchlab.tradingos.data.TradingOsUiState
import com.ttechnologyresearchlab.tradingos.localization.AppLanguage
import com.ttechnologyresearchlab.tradingos.localization.L
import com.ttechnologyresearchlab.tradingos.ui.components.EmergencyStopButton
import com.ttechnologyresearchlab.tradingos.ui.components.GlassCard
import com.ttechnologyresearchlab.tradingos.ui.components.GoldButton
import com.ttechnologyresearchlab.tradingos.ui.components.KeyValue
import com.ttechnologyresearchlab.tradingos.ui.components.MetricCard
import com.ttechnologyresearchlab.tradingos.ui.components.PerformanceWheel
import com.ttechnologyresearchlab.tradingos.ui.components.PremiumHero
import com.ttechnologyresearchlab.tradingos.ui.components.QuietButton
import com.ttechnologyresearchlab.tradingos.ui.components.ScreenShell
import com.ttechnologyresearchlab.tradingos.ui.components.SignalBar
import com.ttechnologyresearchlab.tradingos.ui.components.StatusChip
import com.ttechnologyresearchlab.tradingos.ui.navigation.AppRoute
import com.ttechnologyresearchlab.tradingos.ui.theme.DangerRed
import com.ttechnologyresearchlab.tradingos.ui.theme.ElectricBlue
import com.ttechnologyresearchlab.tradingos.ui.theme.MutedText
import com.ttechnologyresearchlab.tradingos.ui.theme.SafeGreen
import com.ttechnologyresearchlab.tradingos.ui.theme.PanelBlack
import com.ttechnologyresearchlab.tradingos.ui.theme.TradingGold
import com.ttechnologyresearchlab.tradingos.ui.theme.WarningAmber
import com.ttechnologyresearchlab.tradingos.viewmodel.TradingOsViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TradingOsApp(viewModel: TradingOsViewModel) {
    val state by viewModel.uiState.collectAsState()
    var route by remember { mutableStateOf(AppRoute.Onboarding) }
    var menuExpanded by remember { mutableStateOf(false) }
    val menuRoutes = listOf(
        AppRoute.SetupWizard,
        AppRoute.Dashboard,
        AppRoute.Market,
        AppRoute.BinanceEcosystem,
        AppRoute.Derivatives,
        AppRoute.BotBrain,
        AppRoute.Control,
        AppRoute.Portfolio,
        AppRoute.Decisions,
        AppRoute.Journal,
        AppRoute.Statement,
        AppRoute.Reports,
        AppRoute.SafetyLock,
        AppRoute.License,
        AppRoute.Settings,
        AppRoute.AppLock,
        AppRoute.Audit,
        AppRoute.ReleaseReadiness
    )
    if (state.appLocked) {
        AppLockScreen(state, viewModel::unlockWithPin)
        return
    }
    Scaffold(
        topBar = {
            TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                painter = painterResource(R.mipmap.ic_launcher),
                                contentDescription = "TTRL AI Trading OS",
                                tint = Color.Unspecified,
                                modifier = Modifier.size(34.dp)
                            )
                            Spacer(Modifier.width(10.dp))
                            Column {
                                Text(
                                    route.title,
                                    color = TradingGold,
                                    fontWeight = FontWeight.Bold,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                    fontSize = 20.sp
                                )
                                Text(
                                    "Live DISABLED / Paper Mode",
                                    color = SafeGreen,
                                    maxLines = 1,
                                    overflow = TextOverflow.Ellipsis,
                                    fontSize = 13.sp
                                )
                            }
                        }
                    },
                    actions = {
                        Column {
                            IconButton(
                                onClick = { menuExpanded = true },
                                modifier = Modifier
                                    .size(56.dp)
                                    .padding(end = 6.dp)
                                    .shadow(12.dp, RoundedCornerShape(12.dp))
                            ) {
                                Icon(
                                    Icons.Outlined.Menu,
                                    contentDescription = "Open menu",
                                    tint = TradingGold,
                                    modifier = Modifier.size(40.dp)
                                )
                            }
                            DropdownMenu(
                                expanded = menuExpanded,
                                onDismissRequest = { menuExpanded = false },
                                containerColor = PanelBlack
                            ) {
                                Row(
                                    modifier = Modifier.padding(14.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        painter = painterResource(R.mipmap.ic_launcher),
                                        contentDescription = "TTRL AI Trading OS",
                                        tint = Color.Unspecified,
                                        modifier = Modifier.size(34.dp)
                                    )
                                    Spacer(Modifier.width(10.dp))
                                    Text("TTRL Menu", color = TradingGold, fontWeight = FontWeight.Bold)
                                }
                                menuRoutes.forEach { item ->
                                    DropdownMenuItem(
                                        text = { Text(item.title) },
                                        leadingIcon = { Icon(iconFor(item), contentDescription = item.title) },
                                        onClick = {
                                            route = item
                                            menuExpanded = false
                                        }
                                    )
                                }
                            }
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF080A0F))
                )
            }
    ) { padding ->
        Column(Modifier.padding(padding).fillMaxSize()) {
            when (route) {
                AppRoute.Onboarding -> OnboardingScreen(state, viewModel::completeOnboarding) { route = AppRoute.SetupWizard }
                AppRoute.Splash -> SplashScreen(state, viewModel::refresh)
                AppRoute.SetupWizard -> ApiSetupWizardScreen(
                    state,
                    viewModel::refresh,
                    { route = AppRoute.SafetyLock },
                    { route = AppRoute.Dashboard }
                )
                AppRoute.Dashboard -> DashboardScreen(state, viewModel::emergencyStop)
                AppRoute.Market -> MarketIntelligenceScreen(state)
                AppRoute.BinanceEcosystem -> BinanceEcosystemScreen(state)
                AppRoute.Derivatives -> DerivativesResearchScreen(state)
                AppRoute.BotBrain -> BotBrainScreen(state)
                AppRoute.Control -> TradeControlScreen(state, viewModel)
                AppRoute.Portfolio -> PortfolioScreen(state)
                AppRoute.Decisions -> DecisionsScreen(state)
                AppRoute.Journal -> TradeJournalScreen(state)
                AppRoute.Statement -> StatementScreen(state)
                AppRoute.Reports -> ReportsScreen(state)
                AppRoute.SafetyLock -> SafetyLockScreen(state)
                AppRoute.License -> LicenseActivationScreen(state, viewModel::validateLicense)
                AppRoute.Settings -> SettingsScreen(state, viewModel)
                AppRoute.Audit -> AuditSafetyScreen(state)
                AppRoute.ReleaseReadiness -> ReleaseReadinessScreen(state)
                AppRoute.AppLock -> AppLockSettingsScreen(state, viewModel::lockApp)
            }
        }
    }
}

private fun iconFor(route: AppRoute): ImageVector = when (route) {
    AppRoute.Onboarding -> Icons.Outlined.RocketLaunch
    AppRoute.Splash -> Icons.Outlined.PowerSettingsNew
    AppRoute.SetupWizard -> Icons.Outlined.Tune
    AppRoute.Dashboard -> Icons.Outlined.Dashboard
    AppRoute.Market -> Icons.Outlined.Timeline
    AppRoute.BinanceEcosystem -> Icons.Outlined.Assessment
    AppRoute.Derivatives -> Icons.Outlined.Assessment
    AppRoute.BotBrain -> Icons.Outlined.Psychology
    AppRoute.Control -> Icons.Outlined.Memory
    AppRoute.Portfolio -> Icons.Outlined.PieChart
    AppRoute.Decisions -> Icons.Outlined.Psychology
    AppRoute.Journal -> Icons.Outlined.History
    AppRoute.Statement -> Icons.Outlined.Assessment
    AppRoute.Reports -> Icons.Outlined.Assessment
    AppRoute.SafetyLock -> Icons.Outlined.HealthAndSafety
    AppRoute.License -> Icons.Outlined.VpnKey
    AppRoute.Settings -> Icons.Outlined.Settings
    AppRoute.Audit -> Icons.Outlined.HealthAndSafety
    AppRoute.ReleaseReadiness -> Icons.Outlined.RocketLaunch
    AppRoute.AppLock -> Icons.Outlined.Lock
}

@Composable
fun SplashScreen(state: TradingOsUiState, reconnect: () -> Unit) = ScrollScreen {
    ScreenShell("T AI Trading OS", "Premium paper-mode command center.") {
        PremiumHero(
            title = "TTRL AI Trading OS",
            subtitle = "Backend-controlled paper trading command center with evidence-first market intelligence.",
            primary = "PAPER ACTIVE",
            secondary = "LIVE BLOCKED"
        )
        BackendStatusBanner(state, reconnect)
        MetricCard("AI Trading OS", "BOOT READY", L.text("paper_mode", state.language))
        MetricCard("Safety", state.safetyScore.level, "Score ${state.safetyScore.score}/100")
        MetricCard("Mode", "PAPER", L.text("live_disabled", state.language))
    }
}

@Composable
fun ApiSetupWizardScreen(
    state: TradingOsUiState,
    refresh: () -> Unit,
    openSafetyChecklist: () -> Unit,
    continueDashboard: () -> Unit
) =
    ScrollScreen {
        ScreenShell(L.text("setup_wizard", state.language), "No API key entry in APK. Vault setup remains backend-side.") {
            BackendStatusBanner(state, refresh)
            Checklist(
                listOf(
                    "Backend URL configured: ${state.backendBaseUrl}",
                    "Backend connection status: ${state.connectionStatus}",
                    "API vault status: ${state.settings.vaultStatus}",
                    "Binance readiness: ${state.botStatus.apiReadinessStatus}",
                    "Reading permission expected",
                    "Spot trading permission expected/future",
                    "Withdraw permission OFF required",
                    L.text("paper_mode", state.language),
                    L.text("live_disabled", state.language),
                    "Safety score available: ${state.safetyScore.score}"
                )
            )
            GoldButton("Check Backend Connection", refresh)
            QuietButton("Open Safety Checklist", openSafetyChecklist)
            QuietButton("Continue to Dashboard", continueDashboard)
        }
    }

@Composable
fun DashboardScreen(state: TradingOsUiState, emergencyStop: () -> Unit) = ScrollScreen {
    ScreenShell("Dashboard", "Dashboard/control-first mobile command center.") {
        PremiumHero(
            title = "${state.latestDecision.action} | ${state.latestDecision.confidence}",
            subtitle = state.latestDecision.reason,
            primary = state.botStatus.botState,
            secondary = "Safety ${state.safetyScore.score}/100",
            accent = when (state.latestDecision.action.uppercase()) {
                "BUY" -> SafeGreen
                "SELL" -> DangerRed
                "HOLD" -> WarningAmber
                else -> TradingGold
            }
        )
        BackendStatusBanner(state) {}
        OfflineSyncCard(state)
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Column(Modifier.weight(1f)) {
                MetricCard("Daily Target", "${state.dailyTarget.targetPnlPct}% PnL", state.dailyTarget.recommendedMode)
            }
            Column(Modifier.weight(1f)) {
                MetricCard("Target Progress", "${state.dailyTarget.progressPct}%", "No guarantee")
            }
        }
        PerformanceWheel(
            overallScore = state.performanceWheel.overallScore,
            segments = state.performanceWheel.segments
        )
        CoinUniverseCard(state)
        DailyTargetCard(state)
        TradeQualityCard(state)
        NoTradeZoneCard(state)
        ShadowModeCard(state)
        val connected = state.backendConnectionState == BackendConnectionState.CONNECTED
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Column(Modifier.weight(1f)) { MetricCard("Bot", state.botStatus.botState) }
            Column(Modifier.weight(1f)) { MetricCard("Safety", "${state.safetyScore.score}", state.safetyScore.level) }
        }
        MetricCard("USDT Paper Balance", state.portfolio.paperBalanceUsdt)
        MetricCard("Daily PnL", state.portfolio.dailyPnl)
        MetricCard("Open Paper Trades", state.portfolio.openTrades.toString())
        PaperReadinessCard(state)
        LatestPaperScanCard(state)
        GlassCard {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                StatusChip(state.latestDecision.action, timelineColor(state.latestDecision.action))
                StatusChip("Confidence ${state.latestDecision.confidence}", ElectricBlue)
            }
            Text(state.latestDecision.reason)
            SignalBar("Zero hallucination", state.latestDecision.zeroHallucinationVerified.toString(), SafeGreen)
            SignalBar("Risk gate", state.latestDecision.riskStatus, TradingGold)
        }
        CurrentTradeWatchCard(state)
        DashboardChartsCard(state)
        CandleDetailCard(state.candleDetail)
        CandleStudyCard(state.candleStudies)
        MarketEvidenceFeedCard(state.marketEvidenceFeed.takeLast(5))
        StrategyScoreboardCard(state)
        TimelineCard("Decision Timeline", state.decisionTimeline.takeLast(5))
        EvidenceDrillDownCard(state)
        PaperSessionCard(state)
        PaperScanHistoryCard(state)
        if (connected) {
            EmergencyStopButton(emergencyStop)
        } else {
            MetricCard("Emergency Stop", "Backend offline", "Reconnect before sending stop command.")
        }
    }
}

@Composable
fun MarketIntelligenceScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Market Intelligence", "Evidence-first signals. No unsupported market claims.") {
        PremiumHero(
            title = "Market Intelligence Cockpit",
            subtitle = "Candles, order book, whale, news, structure and risk are shown only when evidence exists.",
            primary = "NO DATA = NO TRADE",
            secondary = "CONFLICT = HOLD/SKIP",
            accent = ElectricBlue
        )
        IntelligenceCard(state)
        CandleDetailCard(state.candleDetail)
        CandleStudyCard(state.candleStudies)
        MarketEvidenceFeedCard(state.marketEvidenceFeed)
        ListCard("Missing data", state.marketIntelligence.missingData)
        ListCard("Conflicts", state.marketIntelligence.conflicts.ifEmpty { listOf("none") })
    }
}

@Composable
fun BinanceEcosystemScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Binance Ecosystem", "Advanced Spot strategy map. Paper/advisory only.") {
        BackendStatusBanner(state) {}
        MetricCard("Exchange scope", "Binance Spot", "No margin / futures / withdrawals")
        MetricCard("Strategy count", state.strategyCatalog.size.toString(), "Backend dynamic catalog")
        MetricCard("Live execution", "BLOCKED", "Backend controls paper intents only")
        ListCard(
            "Master rules",
            listOf(
                "No Data = No Trade",
                "No Proof = No Decision",
                "Conflicts = HOLD/SKIP",
                "Risk unsafe = SKIP",
                "Low confidence = SKIP",
                "External AI key required: no",
                "Phone never places Binance orders"
            )
        )
        state.strategyCatalog.groupBy { it.family }.toSortedMap().forEach { (family, strategies) ->
            DynamicStrategyFamilyCard(family, strategies)
        }
        GlassCard {
            Text("Current bot behavior", color = TradingGold, fontWeight = FontWeight.Bold)
            Text("Decision: ${state.latestDecision.action}")
            Text("Confidence: ${state.latestDecision.confidence}")
            Text("Reason: ${state.latestDecision.reason}")
            Text("Ye screen strategy ecosystem dikhaati hai. Actual paper decision backend evidence aur risk gate se hi aata hai.")
        }
    }
}

@Composable
fun DerivativesResearchScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("F&O Research", "Futures/options are research-only. No leverage execution in this build.") {
        PremiumHero(
            title = "F&O Risk Lab",
            subtitle = "Paper-only derivatives readiness. Designed to show risk before any future audited phase.",
            primary = state.derivatives.mode,
            secondary = "LIVE BLOCKED",
            accent = DangerRed
        )
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Column(Modifier.weight(1f)) {
                MetricCard("Futures execution", state.derivatives.futuresExecutionAvailable.toString())
            }
            Column(Modifier.weight(1f)) {
                MetricCard("Options execution", state.derivatives.optionsExecutionAvailable.toString())
            }
        }
        GlassCard {
            Text("Demo Risk Estimate", color = TradingGold, fontWeight = FontWeight.Bold)
            KeyValue("Notional", state.derivatives.notionalUsdt)
            KeyValue("Leverage", "${state.derivatives.leverage}x", DangerRed)
            KeyValue("Margin estimate", state.derivatives.marginEstimateUsdt)
            KeyValue("Estimated loss on adverse move", state.derivatives.estimatedLossUsdt, DangerRed)
            Text(state.derivatives.liquidationWarning, color = DangerRed)
        }
        ListCard("Allowed F&O features", state.derivatives.allowedFeatures.ifEmpty { listOf("Research only") })
        ListCard("Blocked reasons", state.derivatives.blockedReasons.ifEmpty { listOf("Live derivatives execution blocked") })
        ListCard("Safety notes", state.derivatives.safetyNotes.ifEmpty { listOf("No futures/options real order is sent") })
        GlassCard {
            Text("Decision", color = TradingGold, fontWeight = FontWeight.Bold)
            Text("F&O ko app me education/risk lab ke roop me add kiya gaya hai. Real leverage/margin execution yahan se possible nahi hai.")
            Text("Profit badhane ke liye pehle 18-hour statement, paper win-rate, drawdown, news risk, whale evidence, and candle study stable hona zaroori hai.")
        }
    }
}

@Composable
fun BotBrainScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell(L.text("bot_brain", state.language), "Plain-language decision explanation. No profit guarantees.") {
        PremiumHero(
            title = "Bot Brain Explains Every Move",
            subtitle = state.latestDecision.reason,
            primary = state.latestDecision.action,
            secondary = "Verified ${state.latestDecision.zeroHallucinationVerified}",
            accent = timelineColor(state.latestDecision.action)
        )
        if (state.isPreviewData) MetricCard(L.text("development_preview", state.language), "NOT REAL DATA")
        MetricCard("Latest AI Decision", state.latestDecision.action)
        MetricCard("Confidence", state.latestDecision.confidence)
        IntelligenceCard(state)
        CandleDetailCard(state.candleDetail)
        CandleStudyCard(state.candleStudies)
        MarketEvidenceFeedCard(state.marketEvidenceFeed.takeLast(8))
        EvidenceDrillDownCard(state)
        GlassCard {
            KeyValue("Zero hallucination", state.latestDecision.zeroHallucinationVerified.toString())
            KeyValue("Risk result", state.latestDecision.riskStatus)
            Text("Explanation: ${state.latestDecision.reason}")
            Text(L.text("no_data_no_trade", state.language))
            Text(L.text("conflict_skip_hold", state.language))
        }
        ListCard("Evidence", state.latestDecision.evidence)
    }
}

@Composable
fun TradeControlScreen(state: TradingOsUiState, viewModel: TradingOsViewModel) = ScrollScreen {
    ScreenShell("Trade Control", "Phone controls backend only. It never executes Binance orders.") {
        BackendStatusBanner(state, viewModel::refresh)
        val controlsEnabled = state.backendConnectionState == BackendConnectionState.CONNECTED
        if (controlsEnabled) {
            GoldButton("Start Bot", viewModel::startBot)
            QuietButton("Graceful Stop", viewModel::gracefulStop)
            QuietButton("Pause New Trades", viewModel::pauseNewTrades)
            QuietButton("Resume Paper Trades", viewModel::resumePaperTrades)
            GoldButton("Run Live-Market Paper Demo", viewModel::runLiveMarketPaperDemo)
            GoldButton("Open Manual Paper Demo", viewModel::openManualPaperDemo)
            QuietButton("Close Manual Paper Demo", viewModel::closeManualPaperDemo)
            QuietButton("Simulate Stop-Loss", viewModel::simulateManualStopLoss)
            QuietButton("Simulate Take-Profit", viewModel::simulateManualTakeProfit)
            GoldButton("Start 24x7 Paper Session", viewModel::startPaperSession)
            QuietButton("Stop Paper Session", viewModel::stopPaperSession)
        } else {
            MetricCard("Controls Disabled", "Backend offline", "Reconnect before sending control commands.")
        }
        if (controlsEnabled) {
            EmergencyStopButton(viewModel::emergencyStop)
        } else {
            MetricCard("Emergency Stop", "Backend offline", "No backend command is sent while disconnected.")
        }
        GlassCard {
            KeyValue("Shutdown state", state.shutdownState)
            Text("Graceful stop blocks new trades immediately, keeps active paper trades managed, saves logs, then stops after safe state.")
            Text("Live-market paper demo reads public market data only and never places Binance orders.")
            Text("Manual paper demo opens a capped paper-only position for walkthrough visibility. It is not an AI trade.")
            Text("Close/SL/TP buttons are paper-only lifecycle simulations.")
        }
        PaperReadinessCard(state)
        LatestPaperScanCard(state)
        PaperSessionCard(state)
        PaperScanHistoryCard(state)
    }
}

@Composable
fun SafetyLockScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell(L.text("safety_lock", state.language), "Hard safety boundaries shown before APK release.") {
        MetricCard("Safety Status", state.safetyScore.level, "SAFE / CAUTION / DANGER / UNKNOWN")
        Checklist(
            listOf(
                L.text("live_disabled", state.language),
                L.text("withdrawals_unsupported", state.language),
                L.text("paper_mode", state.language),
                "10% reserve lock",
                "5% max risk rule",
                "Stop-loss required",
                "Take-profit required",
                "Emergency stop enabled",
                "Zero hallucination active",
                L.text("no_data_no_trade", state.language),
                L.text("conflict_skip_hold", state.language)
            )
        )
    }
}

@Composable
fun LicenseActivationScreen(state: TradingOsUiState, validateLicense: (String) -> Unit) = ScrollScreen {
    var licenseKey by remember { mutableStateOf("") }
    ScreenShell(L.text("license_activation", state.language), "TTRL app access only. This is not a Binance API key.") {
        BackendStatusBanner(state) {}
        OutlinedTextField(
            value = licenseKey,
            onValueChange = { licenseKey = it.uppercase().take(24) },
            label = { Text(L.text("app_license_key", state.language)) },
            modifier = Modifier.fillMaxWidth()
        )
        GoldButton(L.text("validate_license", state.language)) {
            validateLicense(licenseKey)
            licenseKey = ""
        }
        GlassCard {
            KeyValue("License status", state.licenseStatus.status, when (state.licenseStatus.status) {
                "ACTIVE" -> SafeGreen
                "BACKEND_OFFLINE" -> TradingGold
                else -> DangerRed
            })
            KeyValue("Key", state.licenseStatus.redactedLicenseKey.ifEmpty { "not entered" })
            KeyValue("Expiry", state.licenseStatus.expiry)
            KeyValue("Remaining activations", state.licenseStatus.remainingActivations)
            Text(state.licenseStatus.message)
        }
        Checklist(
            listOf(
                "App validates TTRL license through backend only",
                "App cannot generate license keys",
                "Binance API keys are configured separately in backend/vault",
                L.text("live_disabled", state.language),
                L.text("withdrawals_unsupported", state.language)
            )
        )
    }
}

@Composable
fun PortfolioScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Portfolio", "Paper portfolio only. No real Binance balance fetch from APK.") {
        MetricCard("Wallet", state.portfolio.paperBalanceUsdt)
        MetricCard("Daily PnL", state.portfolio.dailyPnl)
        MetricCard("Exposure", state.portfolio.exposure)
        MetricCard("Reserve Lock", state.portfolio.reserveLock)
        MetricCard("Drawdown", state.portfolio.drawdown)
        ListCard("Open positions", state.openTrades.map { "${it.symbol} ${it.status} ${it.pnl}" })
        ListCard("Closed positions", state.closedTrades.map { "${it.symbol} ${it.status} ${it.pnl}" })
    }
}

@Composable
fun DecisionsScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("AI Decisions", "BUY / SELL / HOLD / SKIP only. Zero-hallucination verification required.") {
        MetricCard("Latest", state.latestDecision.action)
        MetricCard("Confidence", state.latestDecision.confidence)
        GlassCard {
            Text("Reason", color = TradingGold, fontWeight = FontWeight.Bold)
            Text(state.latestDecision.reason)
            KeyValue("Zero hallucination", state.latestDecision.zeroHallucinationVerified.toString(), if (state.latestDecision.zeroHallucinationVerified) SafeGreen else DangerRed)
            KeyValue("Risk", state.latestDecision.riskStatus)
        }
        ListCard("Evidence", state.latestDecision.evidence)
        EvidenceDrillDownCard(state)
        GlassCard {
            Text("Candle / Whale / News Detail", color = TradingGold, fontWeight = FontWeight.Bold)
            KeyValue("Candle", state.marketIntelligence.candleSignal)
            KeyValue("Whale", state.marketIntelligence.whaleSignal)
            KeyValue("Order book", state.marketIntelligence.orderBookSignal)
            KeyValue("News", state.marketIntelligence.newsRiskSignal)
            KeyValue("Structure", state.marketIntelligence.marketStructureSignal)
            Text("Tap flow target: trade/candle drill-down modal in next UI pass. Current screen already shows backend evidence summaries.")
        }
        ListCard("Missing data", state.latestDecision.missingData)
        ListCard("Conflicts", state.latestDecision.conflicts.ifEmpty { listOf("none") })
    }
}

@Composable
fun TradeJournalScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Trade Journal", "Paper fills, partial exits, stop-loss and take-profit events only.") {
        CurrentTradeWatchCard(state)
        EvidenceDrillDownCard(state)
        TimelineCard("Paper Trade Timeline", state.tradeTimeline)
        ListCard("Open trades", state.openTrades.map { "${it.symbol} ${it.side} ${it.status}" })
        ListCard("Closed trades", state.closedTrades.map { "${it.symbol} ${it.side} ${it.pnl}" })
        ListCard("Journal", state.journal.map { "${it.id} ${it.status} ${it.pnl}" })
        MetricCard("Realized / Unrealized PnL", "${state.portfolio.dailyPnl} / preview")
        ListCard("Audit report", state.auditEvents.map { "${it.type}: ${it.detail}" })
    }
}

@Composable
fun StatementScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Daily Statement", "24-hour and rolling 7-day paper profit/loss statement.") {
        PremiumHero(
            title = "24h Net PnL ${state.statement.netPnl}",
            subtitle = "Daily window: ${state.statement.windowHours} hours | Statement ${state.statement.statementId}",
            primary = "DAILY PAPER STATEMENT",
            secondary = "7D PnL ${state.statement.sevenDayNetPnl}",
            accent = if (state.statement.netPnl.startsWith("-")) DangerRed else SafeGreen
        )
        GlassCard {
            Text("Rolling 7-Day Statement", color = TradingGold, fontWeight = FontWeight.Bold)
            KeyValue("7D Net PnL", state.statement.sevenDayNetPnl, if (state.statement.sevenDayNetPnl.startsWith("-")) DangerRed else SafeGreen)
            KeyValue("7D Realized PnL", state.statement.sevenDayRealizedPnl)
            KeyValue("7D Closed positions", state.statement.sevenDayClosedPositions)
            KeyValue("7D Win rate", "${state.statement.sevenDayWinRatePct}%")
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Column(Modifier.weight(1f)) { MetricCard("Profit", state.statement.grossProfit, "Gross positive PnL") }
            Column(Modifier.weight(1f)) { MetricCard("Loss", state.statement.grossLoss, "Gross negative PnL") }
        }
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
            Column(Modifier.weight(1f)) { MetricCard("Realized", state.statement.realizedPnl) }
            Column(Modifier.weight(1f)) { MetricCard("Unrealized", state.statement.unrealizedPnl) }
        }
        GlassCard {
            Text("Trading Summary", color = TradingGold, fontWeight = FontWeight.Bold)
            KeyValue("Open positions", state.statement.openPositions)
            KeyValue("Closed positions", state.statement.closedPositions)
            KeyValue("Journal entries", state.statement.journalEntries)
            KeyValue("Win rate", "${state.statement.winRatePct}%")
        }
        ListCard("Safety checks", state.statement.safetyChecks.ifEmpty { listOf("Statement safety checks unavailable") })
        ListCard("Statement trades", state.statement.tradeRows.ifEmpty { listOf("No paper trades in this statement window") })
        ListCard("Paper scan decisions", state.statement.paperScanRows.ifEmpty { listOf("No paper scans in this statement window yet") })
        ListCard("Notes", state.statement.notes)
    }
}

@Composable
fun ReportsScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Reports", "Analytics use persisted paper records only.") {
        StatementScreenInline(state)
        DashboardChartsCard(state)
        TimelineCard("Decision Timeline", state.decisionTimeline)
        TimelineCard("Paper Trade Timeline", state.tradeTimeline)
        state.reports.forEach { report ->
            GlassCard {
                Text(report.title, color = TradingGold, fontWeight = FontWeight.Bold)
                Text(report.status)
                Text(report.detail)
            }
        }
    }
}

@Composable
private fun StatementScreenInline(state: TradingOsUiState) {
    GlassCard {
        Text("Daily / 7-Day Statement", color = TradingGold, fontWeight = FontWeight.Bold)
        KeyValue("24h Net PnL", state.statement.netPnl, if (state.statement.netPnl.startsWith("-")) DangerRed else SafeGreen)
        KeyValue("24h Realized", state.statement.realizedPnl)
        KeyValue("7D Net PnL", state.statement.sevenDayNetPnl, if (state.statement.sevenDayNetPnl.startsWith("-")) DangerRed else SafeGreen)
        KeyValue("Closed positions", state.statement.closedPositions)
        Text("Open the Statement screen for full paper profit/loss detail.")
    }
}

@Composable
fun SettingsScreen(state: TradingOsUiState, viewModel: TradingOsViewModel) = ScrollScreen {
    var backendUrl by remember { mutableStateOf(state.backendBaseUrl) }
    ScreenShell("Settings", "No API key submission. No live toggle. No withdrawals.") {
        GlassCard {
            Text("Founder / Architect", color = TradingGold, fontWeight = FontWeight.Bold)
            Text("MOSIN LIYAKAT SHAIKH")
            Text("TTRL AI Trading OS / T Financial Intelligence OS")
        }
        LanguageSelector(state.language, viewModel::updateLanguage)
        OutlinedTextField(
            value = backendUrl,
            onValueChange = {
                backendUrl = it
                viewModel.updateBackendUrl(it)
            },
            label = { Text("Backend URL") },
            modifier = Modifier.fillMaxWidth()
        )
        StrategyControlPanel()
        NotificationSettingsPanel()
        GlassCard {
            KeyValue("Risk reserve", state.settings.risk.reserveCapitalPct)
            KeyValue("Max exposure", state.settings.risk.maxRiskExposurePct)
            KeyValue("Stop loss required", state.settings.risk.stopLossRequired.toString())
            KeyValue("Take profit required", state.settings.risk.takeProfitRequired.toString())
        }
        GlassCard {
            KeyValue("API vault", state.settings.vaultStatus)
            KeyValue("Live trading", state.settings.liveTradingStatus, DangerRed)
            KeyValue("Withdrawals", state.settings.withdrawalsStatus, DangerRed)
            KeyValue("Notifications", state.settings.notifications)
        }
        QuietButton("Lock App", viewModel::lockApp)
    }
}

@Composable
fun AuditSafetyScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell("Audit / Safety", "Runtime, risk, hallucination and config health timeline.") {
        MetricCard("API readiness", state.botStatus.apiReadinessStatus)
        MetricCard("Config health", if (state.botStatus.liveTradingEnabled) "DANGER" else "SAFE")
        ListCard("Safety reasons", state.safetyScore.reasons)
        TimelineCard("Audit Timeline", state.auditTimeline)
        ListCard("Audit timeline", state.auditEvents.map { "${it.timestamp} ${it.type}: ${it.detail}" })
        GlassCard {
            Text("Recommended action", color = TradingGold, fontWeight = FontWeight.Bold)
            Text(state.safetyScore.recommendedAction)
        }
    }
}

@Composable
fun ReleaseReadinessScreen(state: TradingOsUiState) = ScrollScreen {
    ScreenShell(L.text("release_readiness", state.language), "Final APK build remains pending.") {
        Checklist(
            listOf(
                "Architect: MOSIN LIYAKAT SHAIKH",
                "Product: TTRL AI Trading OS / T Financial Intelligence OS",
                "Backend connected: ${state.backendConnectionState}",
                "Database ready: backend verified",
                L.text("paper_mode", state.language),
                L.text("live_disabled", state.language),
                L.text("withdrawals_unsupported", state.language),
                "Monitoring readiness: ${state.paperDemoReadiness.monitoringPercent}%",
                "Paper demo readiness: ${state.paperDemoReadiness.demoPercent}%",
                "Safety score: ${state.safetyScore.score}",
                "Last heartbeat: ${state.lastHeartbeat}",
                "API readiness: ${state.botStatus.apiReadinessStatus}",
                "Audit logging active",
                "No secrets in app",
                "Final APK build pending"
            )
        )
        if (state.paperDemoReadiness.remaining.isNotEmpty()) {
            ListCard("Remaining paper checks", state.paperDemoReadiness.remaining)
        }
    }
}

@Composable
fun AppLockSettingsScreen(state: TradingOsUiState, lockApp: () -> Unit) = ScrollScreen {
    ScreenShell("App Lock", "Dashboard/control access lock only. No Binance secrets are stored here.") {
        MetricCard("Lock status", if (state.appLocked) "LOCKED" else "UNLOCKED")
        Text("4-digit PIN placeholder. Biometric unlock placeholder only.")
        QuietButton("Lock App", lockApp)
    }
}

@Composable
fun AppLockScreen(state: TradingOsUiState, unlock: (String) -> Unit) {
    var pin by remember { mutableStateOf("") }
    ScrollScreen {
        ScreenShell("App Locked", "PIN protects dashboard/control access only.") {
            OutlinedTextField(
                value = pin,
                onValueChange = { pin = it.take(4) },
                label = { Text("4-digit PIN placeholder") },
                modifier = Modifier.fillMaxWidth()
            )
            GoldButton("Unlock", { unlock(pin) })
            Text("No Binance secrets exist in APK source or local lock storage.")
            Text("Biometric unlock placeholder for future phase.")
        }
    }
}

@Composable
fun OnboardingScreen(state: TradingOsUiState, complete: () -> Unit, continueSetup: () -> Unit) = ScrollScreen {
    ScreenShell("Welcome to AI Trading OS", "First-launch safety onboarding.") {
        Checklist(
            listOf(
                "Welcome to AI Trading OS",
                "Paper Mode / Research Mode",
                "No Guaranteed Profit",
                "Backend Required",
                "Withdraw Permission Must Stay OFF",
                "Emergency Stop and Graceful Stop"
            )
        )
        Text("Language: ${state.language.label}. Hinglish is available in Settings.")
        GoldButton("Continue", { complete(); continueSetup() })
        QuietButton("Skip", { complete(); continueSetup() })
    }
}

@Composable
private fun BackendStatusBanner(state: TradingOsUiState, reconnect: () -> Unit) {
    val (label, color) = when (state.backendConnectionState) {
        BackendConnectionState.CONNECTED -> "CONNECTED" to SafeGreen
        BackendConnectionState.DISCONNECTED -> "DISCONNECTED" to DangerRed
        BackendConnectionState.DEGRADED -> "DEGRADED" to TradingGold
        BackendConnectionState.UNKNOWN -> "UNKNOWN" to Color.White
    }
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip(label, color)
            StatusChip("PAPER", SafeGreen)
            StatusChip("NO WITHDRAW", TradingGold)
        }
        KeyValue("Last bot state", state.lastKnownBotState)
        KeyValue("Last heartbeat", state.lastHeartbeat)
        if (state.backendConnectionState != BackendConnectionState.CONNECTED) {
            Text("Backend offline/degraded. Controls are disabled except local navigation.")
            QuietButton("Reconnect", reconnect)
        }
    }
}

@Composable
private fun OfflineSyncCard(state: TradingOsUiState) {
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip("SYNC ${state.offlineSync.status}", when {
                state.offlineSync.status.contains("SYNCED", ignoreCase = true) -> SafeGreen
                state.offlineSync.status.contains("OFFLINE", ignoreCase = true) -> WarningAmber
                else -> ElectricBlue
            })
            StatusChip(state.backendConnectionState.name, timelineColor(state.backendConnectionState.name))
        }
        KeyValue("Last successful sync", state.offlineSync.lastSuccessfulSync)
        KeyValue("Local queued actions", state.offlineSync.queuedLocalActions.toString())
        Text(state.offlineSync.cacheStatus)
        Text("Phone offline ho to last known data dikhega. Internet wapas aate hi Railway se full refresh hoga.")
    }
}

@Composable
private fun CoinUniverseCard(state: TradingOsUiState) {
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip("ALL COINS", ElectricBlue)
            StatusChip("${state.coinUniverse.symbolCount} USDT SPOT", SafeGreen)
        }
        Text("Binance Spot Coin Universe", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        KeyValue("Universe mode", state.coinUniverse.mode)
        KeyValue("Safe scan batch", state.coinUniverse.scanBatchLimit.toString())
        Text(state.coinUniverse.rule)
        val preview = state.coinUniverse.symbolsPreview.take(18)
        if (preview.isNotEmpty()) {
            Text(preview.joinToString("  |  "), color = MutedText)
        }
        Text("Saare active USDT Spot pairs backend ko pata rahenge; scanner rate-limit safe batches me rank karega.")
    }
}

@Composable
private fun DailyTargetCard(state: TradingOsUiState) {
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip("DAILY TARGET ${state.dailyTarget.targetPnlPct}%", WarningAmber)
            StatusChip(state.dailyTarget.recommendedMode, timelineColor(state.dailyTarget.recommendedMode))
        }
        Text("Daily PnL Target Guard", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        SignalBar("Progress", "${state.dailyTarget.progressPct}%", if (state.dailyTarget.targetReached) SafeGreen else ElectricBlue)
        KeyValue("Target amount", state.dailyTarget.targetAmountUsdt)
        KeyValue("Current daily PnL", state.dailyTarget.currentDailyPnlUsdt, if (state.dailyTarget.currentDailyPnlUsdt.startsWith("-")) DangerRed else SafeGreen)
        KeyValue("Target reached", state.dailyTarget.targetReached.toString())
        state.dailyTarget.rules.take(4).forEach { Text("- $it") }
        Text("10% per day target hai, promise nahi. Bot weak/conflicting data me SKIP/HOLD karega.")
    }
}

@Composable
private fun TradeQualityCard(state: TradingOsUiState) {
    GlassCard {
        Text("Trade Quality Score", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        SignalBar("Score", "${state.tradeQuality.score}/100", when {
            state.tradeQuality.score >= 70 -> SafeGreen
            state.tradeQuality.score >= 45 -> WarningAmber
            else -> DangerRed
        })
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip(state.tradeQuality.level, timelineColor(state.tradeQuality.level))
            StatusChip(state.tradeQuality.recommendedAction, timelineColor(state.tradeQuality.recommendedAction))
            StatusChip(if (state.tradeQuality.tradeAllowed) "PAPER WATCH" else "NO TRADE", if (state.tradeQuality.tradeAllowed) SafeGreen else WarningAmber)
            StatusChip(
                if (state.tradeQuality.evidenceSymbolAligned) "FRESH EVIDENCE" else "STALE EVIDENCE",
                if (state.tradeQuality.evidenceSymbolAligned) SafeGreen else DangerRed
            )
        }
        KeyValue("Latest scan symbol", state.tradeQuality.latestSymbol)
        KeyValue("Evidence time", state.tradeQuality.latestTimestamp)
        Text(state.tradeQuality.reason)
        if (state.tradeQuality.warnings.isNotEmpty()) {
            state.tradeQuality.warnings.take(3).forEach { Text("Warning: $it", color = DangerRed) }
        }
        if (state.tradeQuality.missingData.isNotEmpty()) {
            Text("Missing: ${state.tradeQuality.missingData.take(5).joinToString()}", color = WarningAmber)
        }
        if (state.tradeQuality.conflicts.isNotEmpty()) {
            Text("Conflicts: ${state.tradeQuality.conflicts.take(5).joinToString()}", color = DangerRed)
        }
        Text("High quality ka matlab guarantee nahi. Ye sirf paper decision filter hai.")
    }
}

@Composable
private fun NoTradeZoneCard(state: TradingOsUiState) {
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip(state.noTradeZone.zone, if (state.noTradeZone.active) DangerRed else SafeGreen)
            StatusChip(state.noTradeZone.recommendedAction, timelineColor(state.noTradeZone.recommendedAction))
        }
        Text("No-Trade Zone Detector", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        if (state.noTradeZone.reasons.isEmpty()) {
            Text("No major no-trade reason reported.")
        } else {
            state.noTradeZone.reasons.take(6).forEach { Text("- $it") }
        }
        Text("Sideways, low-confidence, ya conflicting market me bot paper trade avoid karega.")
    }
}

@Composable
private fun ShadowModeCard(state: TradingOsUiState) {
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip(state.shadowMode.mode, ElectricBlue)
            StatusChip("WOULD ${state.shadowMode.wouldDo}", timelineColor(state.shadowMode.wouldDo))
        }
        Text("Paper Shadow-Mode Monitoring", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        KeyValue("Enabled", state.shadowMode.enabled.toString(), SafeGreen)
        KeyValue("No-trade zone", state.shadowMode.noTradeZoneActive.toString(), if (state.shadowMode.noTradeZoneActive) WarningAmber else SafeGreen)
        Text(state.shadowMode.reason)
        Text("Ye bot ka rehearsal mode hai: would-buy/would-sell record hota hai, real order nahi.")
    }
}

@Composable
private fun StrategyScoreboardCard(state: TradingOsUiState) {
    GlassCard {
        Text("Strategy Scoreboard", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        if (state.strategyCatalog.isEmpty()) {
            Text("Strategy catalog unavailable.")
        } else {
            state.strategyCatalog.take(6).forEachIndexed { index, strategy ->
                val score = when {
                    strategy.name.contains("CANDLE", ignoreCase = true) -> state.performanceWheel.segments.find { it.name.contains("Candle") }?.score ?: 0
                    strategy.name.contains("WHALE", ignoreCase = true) -> state.performanceWheel.segments.find { it.name.contains("Whale") }?.score ?: 0
                    strategy.name.contains("NEWS", ignoreCase = true) -> state.performanceWheel.segments.find { it.name.contains("News") }?.score ?: 0
                    strategy.name.contains("ORDER", ignoreCase = true) -> state.performanceWheel.segments.find { it.name.contains("Order") }?.score ?: 0
                    else -> state.performanceWheel.overallScore
                }
                KeyValue("${index + 1}. ${strategy.name}", "$score% ${strategy.status}", if (score >= 70) SafeGreen else WarningAmber)
                Text(strategy.purpose, color = MutedText, maxLines = 2)
            }
        }
        Text("Scoreboard advisory hai. Strategy rules backend/paper controlled rahenge.")
    }
}

@Composable
private fun IntelligenceCard(state: TradingOsUiState) {
    GlassCard {
        Text("Signal Matrix", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        SignalBar("Candle", state.marketIntelligence.candleSignal, timelineColor(state.marketIntelligence.candleSignal))
        SignalBar("Order book", state.marketIntelligence.orderBookSignal, ElectricBlue)
        SignalBar("Whale", state.marketIntelligence.whaleSignal, WarningAmber)
        SignalBar("News risk", state.marketIntelligence.newsRiskSignal, timelineColor(state.marketIntelligence.newsRiskSignal))
        SignalBar("Structure", state.marketIntelligence.marketStructureSignal, SafeGreen)
        KeyValue("Combined confidence", state.marketIntelligence.combinedConfidence, TradingGold)
    }
}

@Composable
private fun CurrentTradeWatchCard(state: TradingOsUiState) {
    val activeTrade = state.openTrades.firstOrNull()
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip("TRADE WATCH", TradingGold)
            StatusChip(if (activeTrade == null) "NO OPEN PAPER" else activeTrade.status, if (activeTrade == null) WarningAmber else SafeGreen)
        }
        Text("Bot kya soch raha hai, kya trade open hai, aur kyun hold/skip kar raha hai.", color = Color.White, fontWeight = FontWeight.SemiBold)
        if (activeTrade == null) {
            KeyValue("Trade intent", state.latestDecision.action, TradingGold)
            KeyValue("Status", "No open paper trade")
            KeyValue("Rule", "No Data = No Trade")
            Text("Agar backend evidence missing bhejta hai to decision SKIP rahega. Live trade app se execute nahi hota.")
        } else {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                StatusChip(activeTrade.symbol, TradingGold)
                StatusChip(activeTrade.side, timelineColor(activeTrade.side))
                StatusChip("PnL ${activeTrade.pnl}", SafeGreen)
            }
            KeyValue("Status", activeTrade.status)
            KeyValue("PnL", activeTrade.pnl)
            Text("Paper position backend ke risk/exit rules se manage hoti hai.")
        }
        Text("Evidence being used", color = TradingGold, fontWeight = FontWeight.Bold)
        state.latestDecision.evidence.ifEmpty { listOf("unknown / insufficient data") }.forEach { Text("- $it") }
        Text("Market intelligence details", color = TradingGold, fontWeight = FontWeight.Bold)
        Text("- Candle: ${state.marketIntelligence.candleSignal}")
        Text("- Whale: ${state.marketIntelligence.whaleSignal}")
        Text("- Order book: ${state.marketIntelligence.orderBookSignal}")
        Text("- News: ${state.marketIntelligence.newsRiskSignal}")
        Text("- Structure: ${state.marketIntelligence.marketStructureSignal}")
        Text("Missing / blocked reasons", color = TradingGold, fontWeight = FontWeight.Bold)
        state.latestDecision.missingData.ifEmpty { listOf("none") }.forEach { Text("- $it") }
    }
}

@Composable
private fun PaperReadinessCard(state: TradingOsUiState) {
    GlassCard {
        Text("Paper Demo Readiness", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        SignalBar("Backend + APK monitoring", "${state.paperDemoReadiness.monitoringPercent}%", SafeGreen)
        SignalBar("Paper demo", "${state.paperDemoReadiness.demoPercent}%", SafeGreen)
        StatusChip(if (state.paperDemoReadiness.readyForPaperDemo) "READY" else "NOT READY", if (state.paperDemoReadiness.readyForPaperDemo) SafeGreen else WarningAmber)
        Text("Target for this phase is paper-only 100%. Real-money trading remains blocked.")
    }
}

@Composable
private fun LatestPaperScanCard(state: TradingOsUiState) {
    val scan = state.paperScanSummary
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip("LATEST SCAN", TradingGold)
            StatusChip(scan.action, timelineColor(scan.action))
        }
        KeyValue("Symbol / TF", "${scan.symbol} ${scan.timeframe}", TradingGold)
        KeyValue("Status", scan.status)
        SignalBar("Confidence", scan.confidence, timelineColor(scan.action))
        KeyValue("Trade allowed", scan.tradeAllowed.toString())
        KeyValue("Run count", scan.runCount.toString())
        Text(scan.reason)
        Text("Why not traded: ${scan.whyNotTraded}")
        Text("Timestamp: ${scan.timestamp}")
    }
}

@Composable
private fun EvidenceDrillDownCard(state: TradingOsUiState) {
    GlassCard {
        Text("Trade / Candidate Drill-Down", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip(state.paperSession.bestCandidate, TradingGold)
            StatusChip(state.paperSession.bestAction, timelineColor(state.paperSession.bestAction))
        }
        KeyValue("Candidate", state.paperSession.bestCandidate, TradingGold)
        KeyValue("Candidate action", state.paperSession.bestAction)
        KeyValue("Candidate confidence", state.paperSession.bestConfidence)
        Text(state.paperSession.lastReason)
        Text("Decision layers", color = TradingGold, fontWeight = FontWeight.Bold)
        DrillDownRow("AI", state.latestDecision.action, state.latestDecision.reason)
        DrillDownRow("Candle", signalStatus(state.marketIntelligence.candleSignal), state.marketIntelligence.candleSignal)
        DrillDownRow("Order book", signalStatus(state.marketIntelligence.orderBookSignal), state.marketIntelligence.orderBookSignal)
        DrillDownRow("Whale", signalStatus(state.marketIntelligence.whaleSignal), state.marketIntelligence.whaleSignal)
        DrillDownRow("News", signalStatus(state.marketIntelligence.newsRiskSignal), state.marketIntelligence.newsRiskSignal)
        DrillDownRow("Structure", signalStatus(state.marketIntelligence.marketStructureSignal), state.marketIntelligence.marketStructureSignal)
        DrillDownRow("Risk", state.latestDecision.riskStatus, "Risk approval/rejection is backend controlled.")
        Text("Evidence", color = TradingGold, fontWeight = FontWeight.Bold)
        state.latestDecision.evidence.ifEmpty { listOf("unknown / insufficient data") }.take(6).forEach {
            Text("- $it")
        }
        if (state.latestDecision.conflicts.isNotEmpty()) {
            Text("Conflicts", color = TradingGold, fontWeight = FontWeight.Bold)
            state.latestDecision.conflicts.take(6).forEach { Text("- $it") }
        }
        if (state.latestDecision.missingData.isNotEmpty()) {
            Text("Missing data", color = TradingGold, fontWeight = FontWeight.Bold)
            state.latestDecision.missingData.take(6).forEach { Text("- $it") }
        }
        Text("Rule: missing data or strong conflict means HOLD/SKIP. Phone never executes Binance orders.")
    }
}

@Composable
private fun DashboardChartsCard(state: TradingOsUiState) {
    GlassCard {
        Text("Paper Analytics Board", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        Text("Decision mix", color = TradingGold)
        ChartBar("BUY", state.dashboardCharts.buyCount, TradingGold)
        ChartBar("SELL", state.dashboardCharts.sellCount, DangerRed)
        ChartBar("HOLD", state.dashboardCharts.holdCount, SafeGreen)
        ChartBar("SKIP", state.dashboardCharts.skipCount, Color.White)
        Text("Confidence profile", color = TradingGold)
        ChartBar("High", state.dashboardCharts.highConfidence, SafeGreen)
        ChartBar("Medium", state.dashboardCharts.mediumConfidence, TradingGold)
        ChartBar("Low", state.dashboardCharts.lowConfidence, DangerRed)
        KeyValue("Average confidence", state.dashboardCharts.averageConfidence)
        KeyValue("Paper scans", state.paperSession.scanCount.toString())
    }
}

@Composable
private fun ChartBar(label: String, value: Int, color: Color) {
    val width = ((value.coerceAtLeast(0) + 1).coerceAtMost(25)) / 25f
    Column {
        KeyValue(label, value.toString(), color)
        Box(
            Modifier
                .fillMaxWidth()
                .height(8.dp)
                .background(Color(0xFF20242E), RoundedCornerShape(4.dp))
        ) {
            Box(
                Modifier
                    .fillMaxWidth(width)
                    .height(8.dp)
                    .background(color, RoundedCornerShape(4.dp))
            )
        }
    }
}

@Composable
private fun TimelineCard(title: String, events: List<TimelineEventUi>) {
    GlassCard {
        Text(title, color = TradingGold, fontWeight = FontWeight.Bold)
        if (events.isEmpty()) {
            Text("unknown / insufficient data")
        } else {
            events.takeLast(8).forEach { event ->
                KeyValue(event.title, event.status, timelineColor(event.status))
                Text("${event.timestamp} | ${event.detail}")
            }
        }
        Text("Paper/audit data only. No phone-side Binance execution.")
    }
}

@Composable
private fun MarketEvidenceFeedCard(items: List<MarketEvidenceUi>) {
    GlassCard {
        Text("Market Evidence Feed", color = TradingGold, fontWeight = FontWeight.Bold)
        if (items.isEmpty()) {
            Text("unknown / insufficient data")
        } else {
            items.takeLast(8).forEach { item ->
                KeyValue("${item.layer} ${item.symbol}".trim(), item.signal, timelineColor(item.signal))
                Text("${item.timestamp} | confidence=${item.confidence} | source=${item.source}")
                Text(item.summary)
                if (item.missingData.isNotEmpty()) {
                    Text("Missing: ${item.missingData.take(3).joinToString()}", color = TradingGold)
                }
                if (item.conflicts.isNotEmpty()) {
                    Text("Conflicts: ${item.conflicts.take(3).joinToString()}", color = DangerRed)
                }
            }
        }
        Text("Evidence only. If data is missing, backend returns HOLD/SKIP.")
    }
}

@Composable
private fun CandleDetailCard(candle: CandleDetailUi) {
    GlassCard {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip("CANDLE DETAIL", TradingGold)
            StatusChip(candle.timeframe, ElectricBlue)
        }
        KeyValue("Symbol / TF", "${candle.symbol} ${candle.timeframe}", TradingGold)
        KeyValue("Trend", candle.trend, timelineColor(candle.trend))
        KeyValue("Latest close", candle.latestClose)
        KeyValue("Range high", candle.rangeHigh)
        KeyValue("Range low", candle.rangeLow)
        KeyValue("Volume total", candle.volumeTotal)
        KeyValue("Candles", candle.candleCount.toString())
        KeyValue("Source", candle.source)
        if (candle.sparklineCloses.isNotEmpty()) {
            Text("Close trail", color = TradingGold, fontWeight = FontWeight.Bold)
            Text(candle.sparklineCloses.joinToString(" -> "))
        }
        if (candle.missingData.isNotEmpty()) {
            Text("Missing: ${candle.missingData.joinToString()}", color = DangerRed)
        }
        Text(candle.decisionRule)
        Text("Read-only paper evidence. Phone does not execute Binance orders.")
    }
}

@Composable
private fun CandleStudyCard(studies: List<CandleStudyUi>) {
    GlassCard {
        Text("Deep Candle Study", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 18.sp)
        Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
            listOf("5m", "10m", "1h").forEach { StatusChip(it, ElectricBlue) }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(7.dp)) {
            listOf("4h", "8h", "24h", "1M").forEach { StatusChip(it, TradingGold) }
        }
        Text("Har timeframe par system batata hai candle upar/niche kyun gayi. Evidence-based learning only.")
        if (studies.isEmpty()) {
            Text("Candle study unavailable. Run paper scan or reconnect backend.", color = DangerRed)
        } else {
            studies.take(7).forEach { study ->
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .background(Color(0xFF111B2A), RoundedCornerShape(8.dp))
                        .padding(10.dp),
                    verticalArrangement = Arrangement.spacedBy(7.dp)
                ) {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        StatusChip(study.timeframe, ElectricBlue)
                        StatusChip(study.trend, timelineColor(study.trend))
                    }
                    SignalBar("Confidence", study.confidence, timelineColor(study.trend))
                    Text(study.moveReason, color = Color.White, fontWeight = FontWeight.SemiBold)
                    study.learningNotes.take(2).forEach { note ->
                        Text("Learning: $note", color = MutedText)
                    }
                    if (study.missingData.isNotEmpty()) {
                        Text("Missing: ${study.missingData.joinToString()}", color = DangerRed)
                    }
                }
            }
        }
        Text("No Data = No Trade. Learning advisory hai, live trading enable nahi karta.")
    }
}

private fun timelineColor(status: String): Color = when {
    status.contains("BUY", ignoreCase = true) -> SafeGreen
    status.contains("UPTREND", ignoreCase = true) -> SafeGreen
    status.contains("SELL", ignoreCase = true) -> DangerRed
    status.contains("DOWNTREND", ignoreCase = true) -> DangerRed
    status.contains("SKIP", ignoreCase = true) -> TradingGold
    status.contains("BLOCK", ignoreCase = true) -> DangerRed
    else -> Color.White
}

@Composable
private fun DrillDownRow(layer: String, status: String, detail: String) {
    GlassCard {
        KeyValue(layer, status, when {
            status.contains("BUY", ignoreCase = true) -> SafeGreen
            status.contains("SELL", ignoreCase = true) -> DangerRed
            status.contains("SKIP", ignoreCase = true) -> TradingGold
            status.contains("unknown", ignoreCase = true) -> Color.White
            else -> TradingGold
        })
        Text(detail.ifBlank { "unknown / insufficient data" })
    }
}

private fun signalStatus(value: String): String {
    val upper = value.uppercase()
    return when {
        upper.contains("BUY") || upper.contains("BULL") || upper.contains("UPTREND") -> "BULLISH / WATCH"
        upper.contains("SELL") || upper.contains("BEAR") || upper.contains("DOWNTREND") -> "BEARISH / WATCH"
        upper.contains("RISK") || upper.contains("REGULATORY") || upper.contains("EMERGENCY") -> "RISK / SKIP"
        upper.contains("UNKNOWN") || upper.isBlank() -> "unknown"
        else -> "NEUTRAL / HOLD"
    }
}

@Composable
private fun PaperSessionCard(state: TradingOsUiState) {
    GlassCard {
        Text("24x7 Paper Session", color = TradingGold, fontWeight = FontWeight.Bold)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            StatusChip(if (state.paperSession.running) "RUNNING" else "STOPPED", if (state.paperSession.running) SafeGreen else WarningAmber)
            StatusChip(if (state.paperSession.autoResumeEnabled) "AUTO-RESUME ON" else "AUTO-RESUME OFF", if (state.paperSession.autoResumeEnabled) SafeGreen else WarningAmber)
            StatusChip(if (state.paperSession.liveTradingEnabled) "LIVE ENABLED" else "LIVE DISABLED", if (state.paperSession.liveTradingEnabled) DangerRed else SafeGreen)
        }
        KeyValue("Session ID", state.paperSession.sessionId.ifBlank { "not started" })
        KeyValue("Started at", state.paperSession.startedAt.ifBlank { "not started" })
        KeyValue("Symbols", state.paperSession.symbols.joinToString().ifBlank { "not configured" })
        if (state.paperSession.desiredSymbols.isNotEmpty()) {
            KeyValue("Auto-resume symbols", state.paperSession.desiredSymbols.joinToString())
        }
        KeyValue("Timeframe", state.paperSession.timeframe)
        KeyValue("Interval", "${state.paperSession.intervalSeconds}s")
        KeyValue("Scan count", state.paperSession.scanCount.toString())
        KeyValue("Best candidate", state.paperSession.bestCandidate, TradingGold)
        KeyValue("Action", state.paperSession.bestAction)
        KeyValue("Confidence", state.paperSession.bestConfidence)
        Text(state.paperSession.lastReason)
        Text("Public data only: ${state.paperSession.publicDataOnly}. Paper mode only. Phone does not place Binance orders.")
    }
}

@Composable
private fun PaperScanHistoryCard(state: TradingOsUiState) {
    GlassCard {
        Text("Paper Session History", color = TradingGold, fontWeight = FontWeight.Bold)
        if (state.paperScanHistory.isEmpty()) {
            Text("No paper scans loaded yet. Start paper session or tap refresh.")
        } else {
            state.paperScanHistory.takeLast(20).reversed().forEach { row ->
                GlassCard {
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        StatusChip(row.symbol, TradingGold)
                        StatusChip(row.action, timelineColor(row.action))
                        StatusChip(
                            if (row.tradeAllowed) "PAPER TRADE" else "NO TRADE",
                            if (row.tradeAllowed) SafeGreen else WarningAmber
                        )
                    }
                    KeyValue("Confidence", row.confidence)
                    KeyValue("Timeframe", row.timeframe.ifBlank { "unknown" })
                    KeyValue("Time", row.timestamp)
                    Text(row.whyNotTraded, color = MutedText)
                    if (row.strategyBreakdown.isNotEmpty()) {
                        row.strategyBreakdown.take(5).forEach { Text("- $it", color = MutedText) }
                    }
                }
            }
        }
        Text("History is paper/audit only. No real Binance order is sent from this app.")
    }
}

@Composable
private fun StrategyControlPanel() {
    GlassCard {
        Text("Strategy Control", color = TradingGold, fontWeight = FontWeight.Bold)
        Checklist(
            listOf(
                "Whale Confirmation Strategy: paper/backend controlled",
                "Candle Structure Strategy: paper/backend controlled",
                "News Risk Filter Strategy: paper/backend controlled",
                "Order Book Liquidity Strategy: paper/backend controlled",
                "Multi-Factor AI Strategy: paper/backend controlled"
            )
        )
        Text("Toggles are UI/settings placeholders only. No live trading impact.")
    }
}

@Composable
private fun NotificationSettingsPanel() {
    GlassCard {
        Text("Notification Settings", color = TradingGold, fontWeight = FontWeight.Bold)
        Checklist(
            listOf(
                "Trade signal alert",
                "Trade skipped alert",
                "Risk rejection alert",
                "Hallucination blocked alert",
                "Emergency stop alert",
                "Daily report alert",
                "Bot offline alert",
                "Runtime heartbeat alert",
                "Telegram / WhatsApp / Email adapters remain backend placeholders"
            )
        )
    }
}

@Composable
private fun DynamicStrategyFamilyCard(
    title: String,
    strategies: List<com.ttechnologyresearchlab.tradingos.data.StrategyCatalogUi>
) {
    GlassCard {
        Text(title, color = TradingGold, fontWeight = FontWeight.Bold)
        strategies.forEach { strategy ->
            Text("- ${strategy.name}", fontWeight = FontWeight.Bold)
            Text(strategy.purpose)
            Text("Needs: ${strategy.requiredData.take(4).joinToString()}")
        }
        Text("Status: PAPER_ADVISORY | Evidence required | No live execution")
    }
}

@Composable
private fun LanguageSelector(language: AppLanguage, update: (AppLanguage) -> Unit) {
    GlassCard {
        Text("Language", color = TradingGold, fontWeight = FontWeight.Bold)
        KeyValue("Current", language.label)
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Column(Modifier.weight(1f)) { QuietButton("English") { update(AppLanguage.English) } }
            Column(Modifier.weight(1f)) { QuietButton("Hinglish") { update(AppLanguage.Hinglish) } }
        }
    }
}

@Composable
private fun Checklist(items: List<String>) {
    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
        items.forEach { Text("- $it") }
    }
}

@Composable
private fun ScrollScreen(content: @Composable () -> Unit) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        content()
    }
}

@Composable
private fun ListCard(title: String, items: List<String>) {
    GlassCard {
        Text(title, color = TradingGold, fontWeight = FontWeight.Bold)
        if (items.isEmpty()) {
            Text("unknown / insufficient data", color = Color.White)
        } else {
            items.forEach { Text(it) }
        }
    }
}
