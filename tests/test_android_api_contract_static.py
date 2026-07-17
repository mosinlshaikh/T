from pathlib import Path
import re

REPO_ROOT = Path(__file__).resolve().parents[1]
ANDROID_CLIENT = (
    REPO_ROOT
    / "android_app"
    / "app"
    / "src"
    / "main"
    / "java"
    / "com"
    / "ttechnologyresearchlab"
    / "tradingos"
    / "network"
    / "BackendApiClient.kt"
)
ROUTES_DIR = REPO_ROOT / "trading_os" / "api" / "routes"


def test_android_client_endpoints_exist_in_canonical_backend_routes() -> None:
    android_paths = _android_client_paths(ANDROID_CLIENT)
    backend_paths = _backend_route_paths(ROUTES_DIR)
    missing = sorted(path for path in android_paths if path not in backend_paths)

    assert missing == []


def test_android_client_has_no_live_trading_or_secret_submission_endpoint() -> None:
    source = ANDROID_CLIENT.read_text(encoding="utf-8")
    lowered = source.lower()

    forbidden_fragments = [
        "/live",
        "enable-live",
        "live-trading",
        "binance_api_key",
        "binance_api_secret",
        "withdraw",
        "futures/order",
        "margin/order",
    ]

    assert [item for item in forbidden_fragments if item in lowered] == []


def _android_client_paths(path: Path) -> set[str]:
    source = path.read_text(encoding="utf-8")
    matches = re.findall(r'(?:get|post|postJson)\(\s*"([^"]+)"', source)
    return {_normalize_client_path(match) for match in matches}


def _backend_route_paths(routes_dir: Path) -> set[str]:
    paths: set[str] = set()
    for route_file in routes_dir.glob("*.py"):
        source = route_file.read_text(encoding="utf-8")
        prefix_match = re.search(r"APIRouter\(\s*prefix=\"([^\"]*)\"", source)
        prefix = prefix_match.group(1) if prefix_match else ""
        for route_path in re.findall(r"@router\.(?:get|post|put|delete)\(\"([^\"]+)\"", source):
            paths.add(_normalize_backend_path(prefix + route_path))
    return paths


def _normalize_client_path(path: str) -> str:
    clean = path.split("?", 1)[0]
    clean = re.sub(r"\$[A-Za-z_][A-Za-z0-9_]*", "{}", clean)
    return clean.rstrip("/") or "/"


def _normalize_backend_path(path: str) -> str:
    clean = re.sub(r"\{[^}]+\}", "{}", path)
    return clean.rstrip("/") or "/"
