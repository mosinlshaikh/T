package com.ttechnologyresearchlab.tradingos.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.PowerSettingsNew
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.ttechnologyresearchlab.tradingos.ui.theme.DangerRed
import com.ttechnologyresearchlab.tradingos.ui.theme.GlassStroke
import com.ttechnologyresearchlab.tradingos.ui.theme.MutedText
import com.ttechnologyresearchlab.tradingos.ui.theme.PanelBlack
import com.ttechnologyresearchlab.tradingos.ui.theme.SafeGreen
import com.ttechnologyresearchlab.tradingos.ui.theme.TradingGold

@Composable
fun ScreenShell(
    title: String,
    subtitle: String = "Paper mode. Live trading disabled.",
    content: @Composable () -> Unit
) {
    Column(
        modifier = Modifier
            .background(
                Brush.verticalGradient(
                    listOf(Color(0xFF080A0F), Color(0xFF10131B), Color(0xFF080A0F))
                )
            )
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(title, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Text(subtitle, color = MutedText, style = MaterialTheme.typography.bodySmall)
        SafetyStrip()
        content()
    }
}

@Composable
fun GlassCard(content: @Composable () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = PanelBlack.copy(alpha = 0.86f)),
        border = BorderStroke(1.dp, GlassStroke),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            content()
        }
    }
}

@Composable
fun MetricCard(label: String, value: String, status: String = "") {
    GlassCard {
        Text(label, color = MutedText, style = MaterialTheme.typography.labelMedium)
        Text(value, color = TradingGold, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        if (status.isNotBlank()) Text(status, color = MutedText, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
fun SafetyStrip() {
    GlassCard {
        Text("Research / paper mode", color = SafeGreen, fontWeight = FontWeight.Bold)
        Text("Live trading DISABLED. Withdrawals UNSUPPORTED. No guaranteed profit. Evidence-first decisions only.", color = MutedText, style = MaterialTheme.typography.bodySmall)
    }
}

@Composable
fun EmergencyStopButton(onClick: () -> Unit) {
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(containerColor = DangerRed),
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(8.dp)
    ) {
        Icon(Icons.Outlined.PowerSettingsNew, contentDescription = "Emergency stop")
        Spacer(Modifier.height(1.dp))
        Text("EMERGENCY STOP", fontWeight = FontWeight.Bold)
    }
}

@Composable
fun GoldButton(text: String, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(containerColor = TradingGold, contentColor = Color.Black),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) { Text(text, fontWeight = FontWeight.Bold) }
}

@Composable
fun QuietButton(text: String, onClick: () -> Unit) {
    OutlinedButton(
        onClick = onClick,
        border = BorderStroke(1.dp, GlassStroke),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier.fillMaxWidth()
    ) { Text(text) }
}

@Composable
fun KeyValue(label: String, value: String, valueColor: Color = Color.White) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(label, color = MutedText)
        Text(value, color = valueColor, fontWeight = FontWeight.SemiBold)
    }
}
