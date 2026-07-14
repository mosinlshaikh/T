package com.ttechnologyresearchlab.tradingos.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ttechnologyresearchlab.tradingos.data.PreviewData
import com.ttechnologyresearchlab.tradingos.data.BackendConnectionState
import com.ttechnologyresearchlab.tradingos.data.LocalDashboardCache
import com.ttechnologyresearchlab.tradingos.data.OfflineSyncUi
import com.ttechnologyresearchlab.tradingos.data.TradingOsRepository
import com.ttechnologyresearchlab.tradingos.data.TradingOsUiState
import com.ttechnologyresearchlab.tradingos.localization.AppLanguage
import com.ttechnologyresearchlab.tradingos.network.BackendApiClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class TradingOsViewModel(application: Application) : AndroidViewModel(application) {
    private val backendBaseUrl = MutableStateFlow("https://t-production-8efc.up.railway.app")
    private val repository = TradingOsRepository(BackendApiClient { backendBaseUrl.value })
    private val localCache = LocalDashboardCache(application.applicationContext)
    private val _uiState = MutableStateFlow(localCache.load())
    val uiState: StateFlow<TradingOsUiState> = _uiState

    init {
        refresh()
    }

    fun updateBackendUrl(url: String) {
        backendBaseUrl.value = url
        _uiState.value = _uiState.value.copy(backendBaseUrl = url)
    }

    fun updateLanguage(language: AppLanguage) {
        _uiState.value = _uiState.value.copy(language = language)
    }

    fun lockApp() {
        _uiState.value = _uiState.value.copy(appLocked = true)
    }

    fun unlockWithPin(pin: String) {
        if (pin.length == 4) {
            _uiState.value = _uiState.value.copy(appLocked = false)
        }
    }

    fun completeOnboarding() {
        _uiState.value = _uiState.value.copy(onboardingComplete = true)
    }

    fun refresh() {
        viewModelScope.launch {
            val current = _uiState.value
            val fresh = repository.refreshDashboard()
            val preserved = if (
                fresh.backendConnectionState == BackendConnectionState.DISCONNECTED &&
                !current.isPreviewData
            ) {
                current.copy(
                    connectionStatus = fresh.connectionStatus.ifBlank { "Backend unavailable. Last known data shown." },
                    backendConnectionState = BackendConnectionState.DISCONNECTED,
                    offlineSync = OfflineSyncUi(
                        status = "OFFLINE_CACHE",
                        lastSuccessfulSync = current.offlineSync.lastSuccessfulSync,
                        queuedLocalActions = 0,
                        cacheStatus = "Last known Railway data shown; reconnect will refresh."
                    )
                )
            } else {
                fresh
            }
            val updated = preserved.copy(
                backendBaseUrl = backendBaseUrl.value,
                language = current.language,
                appLocked = current.appLocked,
                onboardingComplete = current.onboardingComplete
            )
            _uiState.value = updated
            if (updated.backendConnectionState == BackendConnectionState.CONNECTED) {
                localCache.save(updated)
            }
        }
    }

    fun startBot() = viewModelScope.launch { repository.startBot(); refresh() }
    fun gracefulStop() = viewModelScope.launch { repository.gracefulStop(); refresh() }
    fun emergencyStop() = viewModelScope.launch { repository.emergencyStop(); refresh() }
    fun pauseNewTrades() = viewModelScope.launch { repository.pauseNewTrades(); refresh() }
    fun resumePaperTrades() = viewModelScope.launch { repository.resumePaperTrades(); refresh() }
    fun runLiveMarketPaperDemo() = viewModelScope.launch { repository.runLiveMarketPaperDemo(); refresh() }
    fun openManualPaperDemo() = viewModelScope.launch { repository.openManualPaperDemo(); refresh() }
    fun closeManualPaperDemo() = viewModelScope.launch { repository.closeManualPaperDemo(); refresh() }
    fun simulateManualStopLoss() = viewModelScope.launch { repository.simulateManualStopLoss(); refresh() }
    fun simulateManualTakeProfit() = viewModelScope.launch { repository.simulateManualTakeProfit(); refresh() }
    fun startPaperSession() = viewModelScope.launch { repository.startPaperSession(); refresh() }
    fun stopPaperSession() = viewModelScope.launch { repository.stopPaperSession(); refresh() }
    fun validateLicense(licenseKey: String) = viewModelScope.launch {
        val licenseStatus = repository.validateLicense(licenseKey)
        _uiState.value = _uiState.value.copy(licenseStatus = licenseStatus)
    }
}
