# Toast migration

Inventory and dashboard for tracking toast surfaces in `metamask-mobile`.

## What's tracked

1. **Component-library Toast** — files that import `component-library/components/Toast` or call `ToastService.showToast`
2. **BaseNotification** — legacy notification-queue toasts (`NotificationManager.showSimpleNotification` / `showTransactionNotification`) and the components that render `BaseNotification`
3. **MMDS Toast** — files that import `toast` / `Toaster` / `ToastSeverity` from `@metamask/design-system-react-native` (target API)

## Quick start

```bash
# from toast-migration/
python3 scripts/scan-toasts.py
python3 scripts/build-dashboard.py
open dashboard/index.html
```

`scan-toasts.py` defaults to `../metamask-mobile`. Override with `--mobile-root`.

## Outputs

- `data/inventory.json` — machine-readable inventory
- `dashboard/index.html` — filterable dashboard
