package com.ttechnologyresearchlab.tradingos

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.lifecycle.viewmodel.compose.viewModel
import com.ttechnologyresearchlab.tradingos.ui.screens.TradingOsApp
import com.ttechnologyresearchlab.tradingos.ui.theme.TTradingOsTheme
import com.ttechnologyresearchlab.tradingos.viewmodel.TradingOsViewModel

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            TTradingOsTheme {
                val viewModel: TradingOsViewModel = viewModel()
                TradingOsApp(viewModel)
            }
        }
    }
}
