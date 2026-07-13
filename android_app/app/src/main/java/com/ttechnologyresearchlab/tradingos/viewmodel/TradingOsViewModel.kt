package com.ttechnologyresearchlab.tradingos.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ttechnologyresearchlab.tradingos.data.PreviewData
import com.ttechnologyresearchlab.tradingos.data.TradingOsRepository
import com.ttechnologyresearchlab.tradingos.data.TradingOsUiState
import com.ttechnologyresearchlab.tradingos.localization.AppLanguage
import com.ttechnologyresearchlab.tradingos.network.BackendApiClient
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class TradingOsViewModel : ViewModel() {
    private val backendBaseUrl = MutableStateFlow("https://t-production-8efc.up.railway.app")
    private val repository = TradingOsRepository(BackendApiClient { backendBaseUrl.value })
    private val _uiState = MutableStateFlow(PreviewData.state)
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
            _uiState.value = repository.refreshDashboard().copy(
                backendBaseUrl = backendBaseUrl.value,
                language = current.language,
                appLocked = current.appLocked,
                onboardingComplete = current.onboardingComplete
            )
        }
    }

    fun startBot() = viewModelScope.launch { repository.startBot(); refresh() }
    fun gracefulStop() = viewModelScope.launch { repository.gracefulStop(); refresh() }
    fun emergencyStop() = viewModelScope.launch { repository.emergencyStop(); refresh() }
    fun pauseNewTrades() = viewModelScope.launch { repository.pauseNewTrades(); refresh() }
    fun resumePaperTrades() = viewModelScope.launch { repository.resumePaperTrades(); refresh() }
    fun runLiveMarketPaperDemo() = viewModelScope.launch { repository.runLiveMarketPaperDemo(); refresh() }
    fun startPaperSession() = viewModelScope.launch { repository.startPaperSession(); refresh() }
    fun stopPaperSession() = viewModelScope.launch { repository.stopPaperSession(); refresh() }
    fun validateLicense(licenseKey: String) = viewModelScope.launch {
        val licenseStatus = repository.validateLicense(licenseKey)
        _uiState.value = _uiState.value.copy(licenseStatus = licenseStatus)
    }
}
