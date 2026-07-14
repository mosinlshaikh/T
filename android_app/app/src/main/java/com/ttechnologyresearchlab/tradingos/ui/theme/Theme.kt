package com.ttechnologyresearchlab.tradingos.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val TradingGold = Color(0xFF4DD8FF)
val SoftGold = Color(0xFFBFEFFF)
val DeepBlack = Color(0xFF020817)
val PanelBlack = Color(0xFF071527)
val GlassStroke = Color(0x554DD8FF)
val DangerRed = Color(0xFFFF4D5E)
val SafeGreen = Color(0xFF4CE0A7)
val ElectricBlue = Color(0xFF38BDF8)
val VioletPulse = Color(0xFF7C8CFF)
val WarningAmber = Color(0xFFFFB84D)
val MutedText = Color(0xFFA9B8CC)

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
