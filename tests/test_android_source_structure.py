from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
ANDROID_ROOT = REPO_ROOT / "android_app"
APP_ROOT = ANDROID_ROOT / "app"
MAIN_SRC = APP_ROOT / "src" / "main" / "java" / "com" / "ttechnologyresearchlab" / "tradingos"


def test_android_project_structure_contains_required_source_files() -> None:
    required_files = [
        ANDROID_ROOT / "settings.gradle.kts",
        ANDROID_ROOT / "build.gradle.kts",
        ANDROID_ROOT / "gradlew.bat",
        APP_ROOT / "build.gradle.kts",
        APP_ROOT / "src" / "main" / "AndroidManifest.xml",
        MAIN_SRC / "MainActivity.kt",
        MAIN_SRC / "network" / "BackendApiClient.kt",
        MAIN_SRC / "data" / "TradingOsRepository.kt",
        MAIN_SRC / "data" / "PreviewData.kt",
        MAIN_SRC / "localization" / "AppLanguage.kt",
        MAIN_SRC / "ui" / "screens" / "TradingOsScreens.kt",
        MAIN_SRC / "viewmodel" / "TradingOsViewModel.kt",
    ]

    assert [str(path) for path in required_files if not path.exists()] == []


def test_android_build_config_matches_safe_apk_contract() -> None:
    build_gradle = (APP_ROOT / "build.gradle.kts").read_text(encoding="utf-8")
    manifest = (APP_ROOT / "src" / "main" / "AndroidManifest.xml").read_text(encoding="utf-8")

    assert 'namespace = "com.ttechnologyresearchlab.tradingos"' in build_gradle
    assert 'applicationId = "com.ttechnologyresearchlab.tradingos"' in build_gradle
    assert _int_value("minSdk", build_gradle) <= 24
    assert _int_value("targetSdk", build_gradle) >= 34
    assert _int_value("compileSdk", build_gradle) >= 34
    assert "android.permission.INTERNET" in manifest
    assert 'android:allowBackup="false"' in manifest
    assert 'android:exported="true"' in manifest


def test_android_source_has_required_safety_ui_and_preview_labels() -> None:
    source = _android_source_text()

    required_text = [
        "DEVELOPMENT PREVIEW DATA",
        "Live Trading Disabled",
        "Withdrawals Unsupported",
        "Paper Mode Active",
        "Evidence First Decision",
        "License Activation",
        "Backend Connected",
        "Emergency Stop",
        "Graceful Stop",
        "Hinglish",
    ]

    assert [text for text in required_text if text not in source] == []


def test_android_source_contains_no_binance_secret_or_direct_order_execution() -> None:
    source = _android_source_text().lower()
    forbidden_patterns = [
        r"binance_api_key\s*=",
        r"binance_api_secret\s*=",
        r"api[_-]?secret\s*=",
        r"secret[_-]?key\s*=",
        r"/api/v3/order",
        r"/sapi/v1/capital/withdraw",
        r"fapi/",
        r"dapi/",
        r"margin/order",
    ]

    assert [pattern for pattern in forbidden_patterns if re.search(pattern, source)] == []


def _android_source_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (APP_ROOT / "src").rglob("*")
        if path.is_file() and path.suffix in {".kt", ".xml"}
    )


def _int_value(name: str, source: str) -> int:
    match = re.search(rf"{name}\s*=\s*(\d+)", source)
    assert match is not None, f"{name} missing"
    return int(match.group(1))
