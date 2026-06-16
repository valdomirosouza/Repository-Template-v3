#!/usr/bin/env python3
"""Fail if a canary-deployed service has no valid per-service SLO file (ADR-0073).

cd-production.yml resolves ``docs/sre/slo/<service>.yaml`` at runtime and reads its ``canary``
block (error_rate_max, p99_latency_seconds_max, error_budget_min_ratio). A service deployed
WITHOUT that file fails the pipeline with no silent default — so the gap should be caught at PR
time, not at deploy time.

This lint reconciles ``services.yaml`` (the canonical service registry) against the SLO files on
disk. A canary gate only has meaning for request-serving services, so the requirement is
**type-aware**:

* ``api`` / ``frontend`` services  -> a canary SLO file is REQUIRED and validated against the schema
* ``worker`` / ``job`` services     -> EXEMPT (no inbound request traffic to canary-gate)

Exemptions are reported explicitly (never silently skipped) so a future request-serving service is
never quietly excused.

Usage:
    python3 scripts/governance/check_service_slo_files.py

Exit 0 = every canary-deployed service has a valid SLO file; exit 1 = at least one is missing or
malformed (use as a CI gate).
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SERVICES = _REPO_ROOT / "services.yaml"
_SLO_DIR = _REPO_ROOT / "docs" / "sre" / "slo"

# Service types that serve inbound requests and therefore need a canary gate.
_CANARY_TYPES = {"api", "frontend"}
# Service types with no inbound request traffic — a canary error-rate/latency gate is meaningless.
_EXEMPT_TYPES = {"worker", "job"}

_REQUIRED_CANARY_KEYS = ("error_rate_max", "p99_latency_seconds_max", "error_budget_min_ratio")


def _validate_canary(canary: object) -> list[str]:
    """Return a list of problems with a canary block (empty == valid)."""
    problems: list[str] = []
    if not isinstance(canary, dict):
        return ["`canary` block is missing or not a mapping"]
    for key in _REQUIRED_CANARY_KEYS:
        if key not in canary:
            problems.append(f"missing canary.{key}")
            continue
        val = canary[key]
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            problems.append(f"canary.{key} must be a number, got {val!r}")
            continue
        if val <= 0:
            problems.append(f"canary.{key} must be > 0, got {val}")
        if key in ("error_rate_max", "error_budget_min_ratio") and val > 1:
            problems.append(f"canary.{key} is a fraction and must be <= 1, got {val}")
    return problems


def main(argv: list[str] | None = None) -> int:
    if not _SERVICES.exists():
        print(f"ERROR: {_SERVICES} not found", file=sys.stderr)
        return 1

    registry = yaml.safe_load(_SERVICES.read_text(encoding="utf-8")) or {}
    services = registry.get("services", [])
    if not services:
        print("ERROR: no services defined in services.yaml", file=sys.stderr)
        return 1

    errors: list[str] = []
    exempt: list[str] = []
    ok: list[str] = []

    for svc in services:
        name = svc.get("name", "<unnamed>")
        stype = svc.get("type", "<unknown>")

        if stype in _EXEMPT_TYPES:
            exempt.append(f"{name} (type={stype})")
            continue
        if stype not in _CANARY_TYPES:
            errors.append(
                f"{name}: unknown service type '{stype}' — classify it as one of "
                f"{sorted(_CANARY_TYPES | _EXEMPT_TYPES)} and update this lint."
            )
            continue

        slo_file = _SLO_DIR / f"{name}.yaml"
        if not slo_file.exists():
            errors.append(
                f"{name}: no canary SLO file at docs/sre/slo/{name}.yaml "
                f"(required for type={stype}, ADR-0073)"
            )
            continue

        try:
            doc = yaml.safe_load(slo_file.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as exc:
            errors.append(f"{name}: docs/sre/slo/{name}.yaml is not valid YAML: {exc}")
            continue

        service_ok = doc.get("service") == name
        if not service_ok:
            errors.append(
                f"{name}: docs/sre/slo/{name}.yaml has service: "
                f"{doc.get('service')!r}, expected {name!r}"
            )
        canary_problems = _validate_canary(doc.get("canary"))
        for problem in canary_problems:
            errors.append(f"{name}: docs/sre/slo/{name}.yaml {problem}")
        if service_ok and not canary_problems:
            ok.append(name)

    # Always report exemptions so they are an explicit, reviewable decision.
    if exempt:
        print("Exempt from canary SLO requirement (no inbound request traffic):")
        for e in exempt:
            print(f"  - {e}")

    if ok:
        print(f"OK — valid canary SLO file for: {', '.join(sorted(ok))}")

    if errors:
        print("\nService SLO traceability errors (ADR-0073):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"\nOK — all {len(ok)} canary-deployed service(s) have a valid SLO file.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
