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
    private val defaultBackendUrl = "http://127.0.0.1:8000"
    private val localCache = LocalDashboardCache(application.applicationContext)
    private val _uiState = MutableStateFlow(localCache.load())
    private val backendBaseUrl = MutableStateFlow(_uiState.value.backendBaseUrl.ifBlank { defaultBackendUrl })
    private val repository = TradingOsRepository(BackendApiClient { backendBaseUrl.value })
    val uiState: StateFlow<TradingOsUiState> = _uiState

    init {
        refresh()
    }

    fun updateBackendUrl(url: String) {
        val cleaned = url.trim().trimEnd('/')
            .ifBlank { defaultBackendUrl }
        backendBaseUrl.value = cleaned
        _uiState.value = _uiState.value.copy(backendBaseUrl = cleaned)
        localCache.saveUiPreferences(_uiState.value)
    }

    fun updateLanguage(language: AppLanguage) {
        _uiState.value = _uiState.value.copy(language = language)
        localCache.saveUiPreferences(_uiState.value)
    }

    fun lockApp() {
        _uiState.value = _uiState.value.copy(appLocked = true)
        localCache.saveUiPreferences(_uiState.value)
    }

    fun unlockWithPin(pin: String) {
        if (pin.length == 4) {
            _uiState.value = _uiState.value.copy(appLocked = false)
            localCache.saveUiPreferences(_uiState.value)
        }
    }

    fun completeOnboarding() {
        _uiState.value = _uiState.value.copy(onboardingComplete = true)
        localCache.saveUiPreferences(_uiState.value)
    }

    fun refresh() {
        viewModelScope.launch {
            val current = _uiState.value
            val fast = repository.refreshDashboardFast(current)
            val fastUpdated = fast.copy(
                backendBaseUrl = backendBaseUrl.value,
                language = current.language,
                appLocked = current.appLocked,
                onboardingComplete = current.onboardingComplete
            )
            _uiState.value = fastUpdated
            if (fastUpdated.backendConnectionState == BackendConnectionState.CONNECTED) {
                localCache.save(fastUpdated)
            }
            val fresh = repository.refreshDashboard()
            val latestCurrent = _uiState.value
            val preserved = if (
                fresh.backendConnectionState == BackendConnectionState.DISCONNECTED &&
                !latestCurrent.isPreviewData
            ) {
                latestCurrent.copy(
                    connectionStatus = fresh.connectionStatus.ifBlank { "Backend unavailable. Last known data shown." },
                    backendConnectionState = BackendConnectionState.DISCONNECTED,
                    offlineSync = OfflineSyncUi(
                        status = "OFFLINE_CACHE",
                        lastSuccessfulSync = latestCurrent.offlineSync.lastSuccessfulSync,
                        queuedLocalActions = 0,
                        cacheStatus = "Last known backend data shown; reconnect will refresh."
                    )
                )
            } else {
                fresh
            }
            val updated = preserved.copy(
                backendBaseUrl = backendBaseUrl.value,
                language = latestCurrent.language,
                appLocked = latestCurrent.appLocked,
                onboardingComplete = latestCurrent.onboardingComplete
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
