package com.ttechnologyresearchlab.tradingos.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val TradingGold = Color(0xFFD4AF37)
val SoftGold = Color(0xFFFFD76A)
val DeepBlack = Color(0xFF05070C)
val PanelBlack = Color(0xFF0E1420)
val GlassStroke = Color(0x44FFD76A)
val DangerRed = Color(0xFFFF4D5E)
val SafeGreen = Color(0xFF4CE0A7)
val ElectricBlue = Color(0xFF38BDF8)
val VioletPulse = Color(0xFF8B5CF6)
val WarningAmber = Color(0xFFFFB84D)
val MutedText = Color(0xFF9AA4B2)

private val TradingColorScheme: ColorScheme = darkColorScheme(
    primary = TradingGold,
    secondary = SoftGold,
    background = DeepBlack,
    surface = PanelBlack,
    error = DangerRed,
    onPrimary = DeepBlack,
    onSecondary = DeepBlack,
    onBackground = Color.White,
    onSurface = Color.White,
    onError = Color.White
)

@Composable
fun TTradingOsTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = TradingColorScheme,
        typography = MaterialTheme.typography,
        content = content
    )
}
