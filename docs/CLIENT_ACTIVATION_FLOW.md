# Client Activation Flow

Client activation belongs to the TTRL AI Trading OS / T Financial Intelligence
OS created and architected by MOSIN LIYAKAT SHAIKH for T TECHNOLOGY RESEARCH
LAB.

1. Owner/admin runs the backend with `TTRL_ADMIN_TOKEN` configured.
2. Owner/admin generates a TTRL app license key from the admin backend route.
3. The full license key is shown once and shared with the client through a safe
   private channel.
4. Client installs the future APK.
5. Client enters the TTRL license key on the License Activation screen.
6. APK calls `POST /license/validate` on the backend.
7. Backend validates status, expiry, device limit, package binding, backend URL
   binding, and optional device fingerprint placeholder.
8. App displays `ACTIVE`, `EXPIRED`, `REVOKED`, `SUSPENDED`, `INVALID`, or
   `BACKEND_OFFLINE`.

Binance API setup is separate. Binance API keys must be created inside Binance
and configured only through the backend/vault process. The APK must not contain
Binance keys, withdrawal support, or direct Binance execution.

## Release Readiness Note

Final APK build is still pending. Activation UI is source-only until the user
gives the explicit build command.
