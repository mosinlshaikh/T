package com.ttechnologyresearchlab.tradingos.localization

enum class AppLanguage(val label: String) {
    English("English"),
    Hinglish("Hinglish")
}

object L {
    fun text(key: String, language: AppLanguage): String {
        return when (language) {
            AppLanguage.English -> english[key] ?: key
            AppLanguage.Hinglish -> hinglish[key] ?: english[key] ?: key
        }
    }

    private val english = mapOf(
        "paper_mode" to "Paper Mode Active",
        "live_disabled" to "Live Trading Disabled",
        "emergency_stop" to "Emergency Stop",
        "backend_connected" to "Backend Connected",
        "backend_disconnected" to "Backend Disconnected",
        "no_data_no_trade" to "No Data = No Trade",
        "conflict_skip_hold" to "Conflict = Skip/Hold",
        "withdrawals_unsupported" to "Withdrawals Unsupported",
        "evidence_first" to "Evidence First Decision",
        "setup_wizard" to "API Setup Wizard",
        "bot_brain" to "Bot Brain",
        "safety_lock" to "Safety Lock",
        "release_readiness" to "Release Readiness",
        "license_activation" to "License Activation",
        "app_license_key" to "TTRL App License Key",
        "validate_license" to "Validate License",
        "license_active" to "License Active",
        "license_invalid" to "License Invalid",
        "backend_offline" to "Backend Offline",
        "development_preview" to "DEVELOPMENT PREVIEW DATA"
    )

    private val hinglish = mapOf(
        "paper_mode" to "Paper Mode Active hai",
        "live_disabled" to "Live Trading Disabled hai",
        "emergency_stop" to "Emergency Stop",
        "backend_connected" to "Backend Connected hai",
        "backend_disconnected" to "Backend Connected nahi hai",
        "no_data_no_trade" to "Data nahi hai = Trade nahi",
        "conflict_skip_hold" to "Conflict hai = Skip ya Hold",
        "withdrawals_unsupported" to "Withdrawals supported nahi hai",
        "evidence_first" to "Evidence ke basis par decision",
        "setup_wizard" to "API Setup Wizard",
        "bot_brain" to "Bot Brain",
        "safety_lock" to "Safety Lock",
        "release_readiness" to "Release Readiness",
        "license_activation" to "License Activation",
        "app_license_key" to "TTRL App License Key",
        "validate_license" to "License validate karo",
        "license_active" to "License Active hai",
        "license_invalid" to "License valid nahi hai",
        "backend_offline" to "Backend Offline hai",
        "development_preview" to "DEVELOPMENT PREVIEW DATA"
    )
}
