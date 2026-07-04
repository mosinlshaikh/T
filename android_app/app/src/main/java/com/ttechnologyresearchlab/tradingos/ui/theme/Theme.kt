package com.ttechnologyresearchlab.tradingos.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.ColorScheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val TradingGold = Color(0xFFD4AF37)
val SoftGold = Color(0xFFFFD76A)
val DeepBlack = Color(0xFF080A0F)
val PanelBlack = Color(0xFF111722)
val GlassStroke = Color(0x33FFD76A)
val DangerRed = Color(0xFFFF4D5E)
val SafeGreen = Color(0xFF4CE0A7)
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
