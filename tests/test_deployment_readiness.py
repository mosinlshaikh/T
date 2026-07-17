from pathlib import Path
import json

from trading_os.api.app import create_app
from trading_os.config import TradingOSConfig

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_railway_and_docker_start_canonical_api() -> None:
    procfile = (REPO_ROOT / "Procfile").read_text(encoding="utf-8")
    dockerfile = (REPO_ROOT / "Dockerfile").read_text(encoding="utf-8")
    railway = json.loads((REPO_ROOT / "railway.json").read_text(encoding="utf-8"))

    assert "trading_os.api.app:app" in procfile
    assert "trading_os.api.app:app" in dockerfile
    assert "uvicorn" in dockerfile
    assert railway["build"]["builder"] == "DOCKERFILE"
    assert railway["deploy"]["healthcheckPath"] == "/status/health"


def test_deployment_config_defaults_are_paper_only_and_safe() -> None:
    config = TradingOSConfig()
    health = config.health_report()

    assert config.runtime_mode.value == "paper"
    assert config.enable_live_trading is False
    assert config.manual_live_unlock is False
    assert config.allow_withdraw_permissions is False
    assert health["config_valid"] is True


def test_env_example_contains_placeholders_only() -> None:
    env_example = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")

    assert "LIVE_TRADING_ENABLED=false" in env_example
    assert "MANUAL_LIVE_UNLOCK=false" in env_example
    assert "BINANCE_WITHDRAWALS_SUPPORTED=false" in env_example
    assert "BINANCE_API_KEY=your_binance_api_key_placeholder" in env_example
    assert "BINANCE_API_SECRET=your_binance_api_secret_placeholder" in env_example


def test_dockerignore_excludes_sensitive_and_generated_files() -> None:
    dockerignore = (REPO_ROOT / ".dockerignore").read_text(encoding="utf-8")
    required_patterns = [
        ".env",
        "*.apk",
        "*.aab",
        "*.exe",
        "*.keystore",
        "*.pem",
        "android_app/app/build/",
        "client_keys/",
        "deployment_secrets/",
        "research_vault/private/",
    ]

    assert [pattern for pattern in required_patterns if pattern not in dockerignore] == []


def test_api_app_imports_for_deployment_without_startup_side_effects() -> None:
    app = create_app()

    assert app is not None
    assert getattr(app, "title", "") == "T AI Binance Trading OS Backend API"
