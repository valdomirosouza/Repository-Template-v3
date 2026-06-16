#!/usr/bin/env python3
"""Fail if the service registry references an artifact that does not exist (traceability gate).

``services.yaml`` is the canonical system-of-record (CLAUDE.md §0.1): every service declares the
ADRs that govern it and the Kafka topics it produces/consumes. A reference that does not resolve is
a silent traceability hole — an auditor, engineer, or agent following the chain hits a dead end.

This lint walks the registry and verifies, for every service:

* each referenced ADR (``ADR-NNNN``) exists as a file under ``docs/adr/``;
* each ``publishes`` / ``subscribes`` topic is defined in the registry's ``topics:`` section;
* each ``depends_on`` target is itself a registered service;

and, for every topic in ``topics:``:

* its ``schema`` Avro file exists on disk;
* its name appears in ``docs/api/asyncapi/v1/asyncapi.yaml`` (CLAUDE.md: a registry topic must have
  a matching AsyncAPI entry).

It does NOT invent a spec column: services do not all declare a spec in the registry, so spec
coverage is tracked in the human-facing docs/governance/traceability-matrix.md, not asserted here.

The AsyncAPI topic-name check is REPORT MODE (warning, ADR-0070 burn-in): ``services.yaml`` and
``docs/api/asyncapi/v1/asyncapi.yaml`` currently use divergent topic-naming schemes (a known gap
tracked in docs/governance/traceability-matrix.md, owned by the Platform team). Pass ``--strict`` to
promote that warning to a blocking error once the drift is reconciled.

Usage:
    python3 scripts/governance/check_traceability.py            # AsyncAPI mismatch = warning
    python3 scripts/governance/check_traceability.py --strict   # AsyncAPI mismatch = error

Exit 0 = every blocking reference resolves; exit 1 = at least one dangling reference (CI gate).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml  # type: ignore[import-untyped]

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SERVICES = _REPO_ROOT / "services.yaml"
_ADR_DIR = _REPO_ROOT / "docs" / "adr"
_ASYNCAPI = _REPO_ROOT / "docs" / "api" / "asyncapi" / "v1" / "asyncapi.yaml"


def _adr_exists(adr_id: str) -> bool:
    """An ADR reference like 'ADR-0002' must resolve to docs/adr/ADR-0002*.md."""
    return bool(list(_ADR_DIR.glob(f"{adr_id}*.md")))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="treat a registry-topic/AsyncAPI naming mismatch as a blocking error (default: warn)",
    )
    args = ap.parse_args(argv)

    if not _SERVICES.exists():
        print(f"ERROR: {_SERVICES} not found", file=sys.stderr)
        return 1

    registry = yaml.safe_load(_SERVICES.read_text(encoding="utf-8")) or {}
    services = registry.get("services", [])
    topics = registry.get("topics", [])
    if not services:
        print("ERROR: no services defined in services.yaml", file=sys.stderr)
        return 1

    service_names = {s.get("name") for s in services}
    topic_names = {t.get("name") for t in topics}
    asyncapi_text = _ASYNCAPI.read_text(encoding="utf-8") if _ASYNCAPI.exists() else None

    errors: list[str] = []
    warnings: list[str] = []

    # ---- service-level references -------------------------------------------------
    for svc in services:
        name = svc.get("name", "<unnamed>")

        for adr in svc.get("adr", []) or []:
            if not _adr_exists(adr):
                errors.append(f"{name}: ADR reference '{adr}' has no file under docs/adr/")

        for direction in ("publishes", "subscribes"):
            for topic in svc.get(direction, []) or []:
                if topic not in topic_names:
                    errors.append(
                        f"{name}: {direction} topic '{topic}' is not defined in services.yaml "
                        f"topics:"
                    )

        for dep in svc.get("depends_on", []) or []:
            if dep not in service_names:
                errors.append(f"{name}: depends_on '{dep}' is not a registered service")

    # ---- topic-level references ---------------------------------------------------
    if asyncapi_text is None:
        errors.append(f"AsyncAPI spec not found at {_ASYNCAPI.relative_to(_REPO_ROOT)}")
    for topic in topics:
        tname = topic.get("name", "<unnamed>")
        schema = topic.get("schema")
        if schema:
            if not (_REPO_ROOT / schema).exists():
                errors.append(f"topic '{tname}': schema file '{schema}' does not exist")
        else:
            errors.append(f"topic '{tname}': no schema declared")
        if asyncapi_text is not None and tname not in asyncapi_text:
            msg = (
                f"topic '{tname}': not referenced in docs/api/asyncapi/v1/asyncapi.yaml "
                f"(CLAUDE.md: registry topics must have a matching AsyncAPI entry)"
            )
            (errors if args.strict else warnings).append(msg)

    if warnings:
        print(
            "Traceability WARNINGS (report mode, ADR-0070 — known gap, see "
            "docs/governance/traceability-matrix.md):",
            file=sys.stderr,
        )
        for w in warnings:
            print(f"  - {w}", file=sys.stderr)
        print("", file=sys.stderr)

    if errors:
        print("Traceability errors in services.yaml:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    suffix = f" ({len(warnings)} warning(s) in report mode)" if warnings else ""
    print(
        f"OK — traceability intact: {len(services)} service(s), {len(topics)} topic(s); "
        f"all blocking ADR, topic, schema and dependency references resolve{suffix}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
