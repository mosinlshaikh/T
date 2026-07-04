# Future APK Phase

The APK is not built in this backend foundation phase.

Future APK role:

- dashboard
- backend control panel
- alerts
- paper reports
- settings
- safety visibility

The APK must not contain Binance API keys, Binance secrets, withdrawal logic, or direct Binance order execution.

The APK will call backend API route skeletons:

- `/api/status`
- `/api/balance`
- `/api/positions`
- `/api/trades`
- `/api/decisions`
- `/api/settings`
- `/api/start`
- `/api/stop`
- `/api/kill-switch`
- `/api/risk`

Final APK build requires a separate explicit command.
