#!/usr/bin/env python3
"""Scan metamask-mobile for component-library, BaseNotification, and MMDS toast usages."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

SKIP = (".test.", ".stories.", "__mocks__", "__snapshots__")
TOAST_IMPORT_RE = re.compile(
    r"from\s+['\"][^'\"]*component-library/components/Toast[^'\"]*['\"]"
)
INVOKE_RE = re.compile(
    r"(?:toastRef(?:\?\.|\.)current(?:\?\.|\.)showToast|ToastService\.showToast|(?<![.\w])showToast)\s*\("
)
PRODUCER_RE = re.compile(
    r"(?:NotificationManager\.)?(?:showSimpleNotification|showTransactionNotification)\s*\("
)
MMDS_IMPORT_RE = re.compile(
    r"import\s*\{([^}]+)\}\s*from\s*['\"]@metamask/design-system-react-native['\"]",
    re.MULTILINE,
)
MMDS_TOAST_INVOKE_RE = re.compile(r"(?<![.\w])toast\s*\(")
MMDS_TOAST_SYMBOLS = frozenset({"toast", "Toaster", "ToastSeverity", "Toast"})
EXCLUDE_TOAST_PREFIXES = (
    "app/component-library/components/Toast/",
    "app/core/ToastService/",
)
BN_INFRA_PREFIXES = (
    "app/core/NotificationManager",
    "app/actions/notification",
    "app/reducers/notification",
)


def parse_codeowners(text: str) -> list[tuple[str, list[str]]]:
    """Parse CODEOWNERS rules in file order. Later matches override earlier ones."""
    rules: list[tuple[str, list[str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        rules.append((parts[0], parts[1:]))
    return rules


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Convert a gitignore-style CODEOWNERS pattern to a full-path regex."""
    if pattern.startswith("/"):
        body = pattern[1:]
        prefix = r"^"
    elif "/" not in pattern.rstrip("/"):
        body = pattern
        prefix = r"(?:^|.*/)"
    else:
        body = pattern
        prefix = r"^"

    regex = prefix
    i = 0
    n = len(body)
    while i < n:
        if body.startswith("**/", i):
            regex += r"(?:.*/)?"
            i += 3
        elif body.startswith("**", i) and i + 2 == n:
            regex += r".*"
            i += 2
        elif body[i] == "*":
            regex += r"[^/]*"
            i += 1
        elif body[i] == "?":
            regex += r"[^/]"
            i += 1
        else:
            regex += re.escape(body[i])
            i += 1
    return re.compile(regex + r"$")


class CodeOwners:
    """Last-matching CODEOWNERS rule wins, matching GitHub's precedence."""

    def __init__(self, text: str):
        self.rules = parse_codeowners(text)
        self._glob_cache: dict[str, re.Pattern[str]] = {}

    def owners_for(self, path: str) -> list[str]:
        path = path.lstrip("/")
        matched: list[str] = []
        for pattern, owners in self.rules:
            if self._matches(path, pattern):
                matched = owners
        return matched

    def _matches(self, path: str, pattern: str) -> bool:
        directory_only = pattern.endswith("/")
        body = pattern[1:] if pattern.startswith("/") else pattern
        body = body.rstrip("/")
        has_magic = bool(re.search(r"[*?[]", body))

        if not has_magic:
            if "/" not in body:
                return (
                    path == body
                    or path.startswith(body + "/")
                    or path.endswith("/" + body)
                    or f"/{body}/" in f"/{path}/"
                )
            return path == body or path.startswith(body + "/")

        glob_pattern = pattern.rstrip("/") if directory_only else pattern
        compiled = self._glob_cache.get(glob_pattern)
        if compiled is None:
            compiled = _glob_to_regex(glob_pattern)
            self._glob_cache[glob_pattern] = compiled
        return compiled.fullmatch(path) is not None


def load_codeowners(mobile_root: Path) -> CodeOwners:
    for candidate in (
        mobile_root / ".github" / "CODEOWNERS",
        mobile_root / "CODEOWNERS",
        mobile_root / "docs" / "CODEOWNERS",
    ):
        if candidate.is_file():
            return CodeOwners(candidate.read_text(errors="ignore"))
    return CodeOwners("")


def attach_codeowners(entries: list[dict], codeowners: CodeOwners) -> None:
    for entry in entries:
        entry["codeowners"] = codeowners.owners_for(entry["file"])


def should_skip(path: Path) -> bool:
    text = str(path)
    return any(token in text for token in SKIP) or path.suffix not in {
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
    }


def area_of(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) >= 4 and parts[0] == "app" and parts[1] == "components":
        if parts[2] in ("UI", "Views", "Nav", "hooks"):
            return f"{parts[2]}/{parts[3]}" if len(parts) > 3 else parts[2]
        return parts[2]
    if len(parts) >= 2:
        return parts[1]
    return "other"


def classify_role(rel: str, text: str) -> str:
    name = Path(rel).name.lower()
    if rel.endswith("App.tsx") or rel.endswith("Root/index.tsx") or "ToastContextWrapper" in text:
        return "host"
    if "toastoptions" in name or name.endswith("toast.ts") or name.endswith("toast.tsx"):
        return "options"
    if "ToastBridge" in rel or "ToastRegistrations" in rel:
        return "bridge"
    return "consumer"


def mmds_symbols(text: str) -> set[str]:
    found: set[str] = set()
    for match in MMDS_IMPORT_RE.finditer(text):
        for raw in match.group(1).split(","):
            name = raw.strip().split(" as ")[0].strip()
            if name in MMDS_TOAST_SYMBOLS:
                found.add(name)
    return found


def classify_mmds_role(symbols: set[str], call_count: int) -> str:
    if "Toaster" in symbols and call_count == 0:
        return "host"
    if "Toaster" in symbols and "toast" not in symbols:
        return "host"
    return "consumer"


def scan_component_library_toasts(app_root: Path) -> list[dict]:
    entries: list[dict] = []
    for path in app_root.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        rel = str(path.relative_to(app_root.parent))
        if rel.startswith(EXCLUDE_TOAST_PREFIXES):
            continue
        text = path.read_text(errors="ignore")
        has_import = bool(TOAST_IMPORT_RE.search(text))
        has_service = "ToastService" in text and (
            "ToastService.showToast" in text
            or bool(re.search(r"from\s+['\"][^'\"]*ToastService", text))
        )
        if not (has_import or has_service):
            continue

        lines = text.splitlines()
        calls: list[dict] = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(("//", "*", "/*")):
                continue
            if re.search(r"showToast\s*[:\?]", stripped) and "(" not in stripped:
                continue
            if INVOKE_RE.search(line) or (
                re.search(r"\.showToast\s*\(", line) and "ToastRef" not in line
            ):
                snippet = "\n".join(lines[i - 1 : min(i + 8, len(lines))])
                labels = re.findall(r"label:\s*['\"]([^'\"]+)['\"]", snippet)
                strings = re.findall(
                    r"(?:title|description|labelOptions).*?['\"]([^'\"]{3,80})['\"]",
                    snippet,
                )
                calls.append(
                    {
                        "line": i,
                        "code": stripped[:180],
                        "hint": labels[0] if labels else (strings[0] if strings else ""),
                    }
                )

        entries.append(
            {
                "file": rel,
                "area": area_of(rel),
                "role": classify_role(rel, text),
                "via": "import" if has_import else "ToastService",
                "callCount": len(calls),
                "calls": calls,
            }
        )
    return sorted(entries, key=lambda e: (-e["callCount"], e["file"]))


def scan_base_notification_consumers(app_root: Path) -> list[dict]:
    entries: list[dict] = []
    for path in app_root.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        rel = str(path.relative_to(app_root.parent))
        if "components-temp/BaseNotification" in rel:
            continue
        text = path.read_text(errors="ignore")
        if "BaseNotification" not in text:
            continue
        usages = []
        for i, line in enumerate(text.splitlines(), 1):
            if "BaseNotification" in line and not line.strip().startswith("//"):
                usages.append({"line": i, "code": line.strip()[:180]})
        entries.append(
            {
                "file": rel,
                "kind": "direct" if "Onboarding" in rel else "wrapper",
                "area": area_of(rel),
                "usages": usages,
            }
        )
    return sorted(entries, key=lambda e: e["file"])


def scan_base_notification_producers(app_root: Path) -> list[dict]:
    entries: list[dict] = []
    for path in app_root.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        rel = str(path.relative_to(app_root.parent))
        if any(rel.startswith(prefix) for prefix in BN_INFRA_PREFIXES):
            continue
        text = path.read_text(errors="ignore")
        lines = text.splitlines()
        hits: list[dict] = []
        for i, line in enumerate(lines, 1):
            if not PRODUCER_RE.search(line):
                continue
            if line.strip().startswith(("//", "*")):
                continue
            snippet = "\n".join(lines[i - 1 : min(i + 12, len(lines))])
            titles = re.findall(r"title:\s*['\"]([^'\"]+)['\"]", snippet)
            descs = re.findall(r"description:\s*['\"]([^'\"]+)['\"]", snippet)
            i18n = re.findall(r"strings\(\s*['\"]([^'\"]+)['\"]", snippet)
            hits.append(
                {
                    "line": i,
                    "kind": "simple" if "Simple" in line else "transaction",
                    "title": titles[0] if titles else "",
                    "description": descs[0] if descs else "",
                    "i18nKeys": i18n[:4],
                    "code": line.strip()[:180],
                }
            )
        if hits:
            entries.append(
                {
                    "file": rel,
                    "area": area_of(rel),
                    "count": len(hits),
                    "hits": hits,
                }
            )
    return sorted(entries, key=lambda e: e["file"])


def scan_mmds_toasts(app_root: Path) -> list[dict]:
    """Files that import MMDS toast / Toaster / ToastSeverity and call toast()."""
    entries: list[dict] = []
    for path in app_root.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        rel = str(path.relative_to(app_root.parent))
        text = path.read_text(errors="ignore")
        symbols = mmds_symbols(text)
        if not symbols:
            continue

        lines = text.splitlines()
        calls: list[dict] = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(("//", "*", "/*")):
                continue
            is_toast_call = bool(MMDS_TOAST_INVOKE_RE.search(line))
            is_toaster_jsx = bool(
                re.match(r"<Toaster(?:\s|/|>)", stripped)
            )
            if not (is_toast_call or is_toaster_jsx):
                continue
            snippet = "\n".join(lines[i - 1 : min(i + 10, len(lines))])
            titles = re.findall(r"title:\s*(?:strings\(\s*)?['\"]([^'\"]+)['\"]", snippet)
            i18n = re.findall(r"strings\(\s*['\"]([^'\"]+)['\"]", snippet)
            severities = re.findall(r"ToastSeverity\.(\w+)", snippet)
            hint = (
                i18n[0]
                if i18n
                else (titles[0] if titles else (severities[0] if severities else ""))
            )
            calls.append(
                {
                    "line": i,
                    "code": stripped[:180],
                    "hint": hint,
                    "kind": "host" if is_toaster_jsx else "call",
                }
            )

        # Skip comment-only Toaster mentions without JSX or toast() usage when
        # the only toast symbol is ToastSeverity with no toast import — keep hosts/consumers.
        if not calls and symbols <= {"ToastSeverity"}:
            continue

        entries.append(
            {
                "file": rel,
                "area": area_of(rel),
                "role": classify_mmds_role(symbols, len(calls)),
                "symbols": sorted(symbols),
                "callCount": sum(1 for c in calls if c["kind"] == "call"),
                "calls": calls,
            }
        )
    return sorted(entries, key=lambda e: (-e["callCount"], e["file"]))


def build_inventory(mobile_root: Path) -> dict:
    app_root = mobile_root / "app"
    if not app_root.is_dir():
        raise SystemExit(f"Expected app/ under {mobile_root}")

    cl = scan_component_library_toasts(app_root)
    bn_consumers = scan_base_notification_consumers(app_root)
    bn_producers = scan_base_notification_producers(app_root)
    mmds = scan_mmds_toasts(app_root)

    codeowners = load_codeowners(mobile_root)
    attach_codeowners(cl, codeowners)
    attach_codeowners(bn_consumers, codeowners)
    attach_codeowners(bn_producers, codeowners)
    attach_codeowners(mmds, codeowners)

    return {
        "sourceRepo": "metamask-mobile",
        "sourcePath": str(app_root),
        "scannedAt": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "componentLibraryToastFiles": len(cl),
            "componentLibraryToastCalls": sum(e["callCount"] for e in cl),
            "componentLibraryByArea": dict(
                Counter(e["area"] for e in cl).most_common()
            ),
            "baseNotificationConsumerFiles": len(bn_consumers),
            "baseNotificationProducerFiles": len(bn_producers),
            "baseNotificationProducerCalls": sum(e["count"] for e in bn_producers),
            "mmdsToastFiles": len(mmds),
            "mmdsToastCalls": sum(e["callCount"] for e in mmds),
            "mmdsByArea": dict(Counter(e["area"] for e in mmds).most_common()),
        },
        "componentLibraryToasts": cl,
        "baseNotificationConsumers": bn_consumers,
        "baseNotificationProducers": bn_producers,
        "mmdsToasts": mmds,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mobile-root",
        type=Path,
        default=Path(__file__).resolve().parents[2] / "metamask-mobile",
        help="Path to metamask-mobile checkout",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "inventory.json",
        help="Output inventory JSON path",
    )
    args = parser.parse_args()

    inventory = build_inventory(args.mobile_root.resolve())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(inventory, indent=2) + "\n")
    print(f"Wrote {args.out}")
    print(json.dumps(inventory["summary"], indent=2))


if __name__ == "__main__":
    main()
