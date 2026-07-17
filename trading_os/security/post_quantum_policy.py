from __future__ import annotations

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class PostQuantumSecurityPolicy:
    """Post-quantum-ready policy metadata.

    This does not claim quantum-proof security. It defines hard controls for
    today's build and the migration boundary for future audited PQC libraries.
    """

    posture: str = "POST_QUANTUM_READY_DESIGN"
    quantum_proof_claimed: bool = False
    app_contains_binance_secrets: bool = False
    repo_contains_secrets: bool = False
    withdrawals_supported: bool = False
    live_trading_enabled: bool = False
    private_key_support: bool = False
    tls_required_for_remote_backend: bool = True
    license_keys_hashed_at_rest: bool = True
    admin_token_from_environment_only: bool = True
    secret_log_redaction_required: bool = True
    recommended_future_pqc: tuple[str, ...] = (
        "hybrid_tls_classical_plus_pqc_when_platform_supported",
        "ml_kem_768_for_future_key_encapsulation_after_library_audit",
        "ml_dsa_or_slhdsa_for_future_release_signing_after_library_audit",
    )
    active_controls: tuple[str, ...] = (
        "paper_mode_default",
        "live_trading_disabled",
        "manual_live_unlock_disabled",
        "withdrawals_blocked",
        "no_binance_secret_in_apk",
        "no_secret_logging",
        "redacted_api_errors",
        "hashed_ttrl_license_keys",
        "admin_license_routes_require_env_token",
        "zero_hallucination_decision_gate",
    )
    limitations: tuple[str, ...] = (
        "Current Android/CPython standard TLS is classical TLS, not full PQC TLS.",
        "No custom cryptography is implemented in this repository.",
        "Production signing keys, API secrets, and client license material must remain private.",
    )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def post_quantum_security_report() -> dict[str, object]:
    return PostQuantumSecurityPolicy().to_dict()
