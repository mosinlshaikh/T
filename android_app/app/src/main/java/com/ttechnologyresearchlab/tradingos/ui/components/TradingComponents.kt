package com.ttechnologyresearchlab.tradingos.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
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
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import androidx.compose.ui.unit.dp
import com.ttechnologyresearchlab.tradingos.data.PerformanceWheelSegmentUi
import com.ttechnologyresearchlab.tradingos.ui.theme.DangerRed
import com.ttechnologyresearchlab.tradingos.ui.theme.DeepBlack
import com.ttechnologyresearchlab.tradingos.ui.theme.ElectricBlue
import com.ttechnologyresearchlab.tradingos.ui.theme.GlassStroke
import com.ttechnologyresearchlab.tradingos.ui.theme.MutedText
import com.ttechnologyresearchlab.tradingos.ui.theme.PanelBlack
import com.ttechnologyresearchlab.tradingos.ui.theme.SafeGreen
import com.ttechnologyresearchlab.tradingos.ui.theme.SoftGold
import com.ttechnologyresearchlab.tradingos.ui.theme.TradingGold
import com.ttechnologyresearchlab.tradingos.ui.theme.WarningAmber

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
                    listOf(DeepBlack, Color(0xFF0B1020), Color(0xFF121827), DeepBlack)
                )
            )
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Text(
                title,
                style = MaterialTheme.typography.headlineSmall,
                color = Color.White,
                fontWeight = FontWeight.Bold,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )
            Text(subtitle, color = MutedText, style = MaterialTheme.typography.bodySmall)
        }
        SafetyStrip()
        content()
    }
}

@Composable
fun GlassCard(content: @Composable () -> Unit) {
    Card(
        colors = CardDefaults.cardColors(containerColor = PanelBlack.copy(alpha = 0.92f)),
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
        Text(label.uppercase(), color = MutedText, style = MaterialTheme.typography.labelSmall)
        Text(value, color = TradingGold, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        if (status.isNotBlank()) Text(status, color = MutedText, style = MaterialTheme.typography.bodySmall, maxLines = 2)
    }
}

@Composable
fun SafetyStrip() {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFF081315), RoundedCornerShape(8.dp))
            .border(1.dp, SafeGreen.copy(alpha = 0.35f), RoundedCornerShape(8.dp))
            .padding(10.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        StatusDot(SafeGreen)
        Column {
            Text("PAPER MODE ACTIVE", color = SafeGreen, fontWeight = FontWeight.Bold, fontSize = 13.sp)
            Text("Live disabled | Withdrawals unsupported | Evidence-first only", color = MutedText, style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
fun EmergencyStopButton(onClick: () -> Unit) {
    Button(
        onClick = onClick,
        colors = ButtonDefaults.buttonColors(containerColor = DangerRed, contentColor = Color.White),
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
        colors = ButtonDefaults.buttonColors(containerColor = SoftGold, contentColor = Color.Black),
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
        Text(label, color = MutedText, modifier = Modifier.weight(1f), maxLines = 2)
        Text(value, color = valueColor, fontWeight = FontWeight.SemiBold, maxLines = 2)
    }
}

@Composable
fun StatusChip(text: String, color: Color = TradingGold) {
    Row(
        modifier = Modifier
            .background(color.copy(alpha = 0.14f), RoundedCornerShape(8.dp))
            .border(1.dp, color.copy(alpha = 0.42f), RoundedCornerShape(8.dp))
            .padding(horizontal = 10.dp, vertical = 7.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        StatusDot(color)
        Text(text, color = color, fontWeight = FontWeight.Bold, fontSize = 12.sp, maxLines = 1)
    }
}

@Composable
fun StatusDot(color: Color) {
    Box(
        modifier = Modifier
            .size(8.dp)
            .background(color, RoundedCornerShape(8.dp))
    )
}

@Composable
fun PremiumHero(
    title: String,
    subtitle: String,
    primary: String,
    secondary: String,
    accent: Color = TradingGold
) {
    Card(
        colors = CardDefaults.cardColors(containerColor = Color.Transparent),
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(1.dp, accent.copy(alpha = 0.42f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .background(
                    Brush.linearGradient(
                        listOf(
                            Color(0xFF082034),
                            Color(0xFF071527),
                            accent.copy(alpha = 0.18f)
                        )
                    )
                )
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                StatusChip(primary, SafeGreen)
                StatusChip(secondary, ElectricBlue)
            }
            Text(title, color = Color.White, fontWeight = FontWeight.Bold, fontSize = 25.sp, lineHeight = 29.sp)
            Text(subtitle, color = MutedText, style = MaterialTheme.typography.bodyMedium)
        }
    }
}

@Composable
fun PerformanceWheel(
    overallScore: Int,
    segments: List<PerformanceWheelSegmentUi>
) {
    val visibleSegments = segments.ifEmpty {
        listOf(PerformanceWheelSegmentUi("No data", 0, "UNKNOWN"))
    }.take(10)
    val colors = listOf(
        ElectricBlue,
        SafeGreen,
        Color(0xFF7C8CFF),
        Color(0xFF22D3EE),
        WarningAmber,
        DangerRed,
        Color.White
    )
    GlassCard {
        Text("Performance Wheel", color = TradingGold, fontWeight = FontWeight.Bold, fontSize = 20.sp)
        Box(Modifier.fillMaxWidth(), contentAlignment = Alignment.Center) {
            Canvas(modifier = Modifier.size(220.dp)) {
                val strokeWidth = 22.dp.toPx()
                val arcSize = size.minDimension - strokeWidth
                val topLeft = androidx.compose.ui.geometry.Offset(strokeWidth / 2, strokeWidth / 2)
                drawCircle(
                    color = Color(0xFF122134),
                    radius = arcSize / 2,
                    style = Stroke(width = strokeWidth)
                )
                val sweepPerSegment = 360f / visibleSegments.size
                visibleSegments.forEachIndexed { index, segment ->
                    val scoreSweep = sweepPerSegment * (segment.score.coerceIn(0, 100) / 100f)
                    drawArc(
                        color = colors[index % colors.size],
                        startAngle = -90f + index * sweepPerSegment,
                        sweepAngle = scoreSweep,
                        useCenter = false,
                        topLeft = topLeft,
                        size = androidx.compose.ui.geometry.Size(arcSize, arcSize),
                        style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                    )
                }
            }
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("${overallScore.coerceIn(0, 100)}", color = Color.White, fontSize = 42.sp, fontWeight = FontWeight.Bold)
                Text("paper score", color = MutedText, fontSize = 12.sp)
            }
        }
        visibleSegments.forEachIndexed { index, segment ->
            Row(
                Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    StatusDot(colors[index % colors.size])
                    Text(segment.name, color = Color.White, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                Text("${segment.score}% ${segment.status}", color = colors[index % colors.size], fontWeight = FontWeight.SemiBold)
            }
        }
        Text("Paper/audit monitoring only. Green segments do not guarantee profit.")
    }
}

@Composable
fun SignalBar(label: String, value: String, color: Color = TradingGold) {
    Column(verticalArrangement = Arrangement.spacedBy(5.dp)) {
        KeyValue(label, value, color)
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .background(Color(0xFF202737), RoundedCornerShape(8.dp))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxWidth(0.62f)
                    .height(6.dp)
                    .background(
                        Brush.horizontalGradient(listOf(color, WarningAmber.copy(alpha = 0.75f))),
                        RoundedCornerShape(8.dp)
                    )
            )
        }
    }
}
