#!/usr/bin/env python3
"""Fail if a runbook link points at a file that does not exist (alert-to-runbook integrity).

Alerts, SLOs and the runbook indexes only help on-call if every link resolves. Runbooks live in two
intentional namespaces (ADR-0033): ``docs/runbooks/`` (RB-NNN, incident response) and
``docs/sre/runbooks/`` (RB-SRE-NNN, SRE operational). This lint does NOT collapse them — it verifies
that every reference, wherever it lives, lands on a real file.

It checks two reference styles:

1. Markdown links in the runbook indexes (``docs/runbooks/README.md``,
   ``docs/sre/runbooks/README.md``) — ``[text](target.md)`` resolved relative to the index file.
2. ``runbook:`` path references in SLO files (``docs/sre/slo/*.yaml``) — resolved relative to the
   repo root.

External links (http/https), pure anchors (``#section``) and ``mailto:`` are ignored.

Usage:
    python3 scripts/governance/check_runbook_links.py

Exit 0 = every runbook reference resolves; exit 1 = at least one dangling reference (CI gate).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]

# Runbook index files whose markdown links we validate.
_INDEX_FILES = [
    _REPO_ROOT / "docs" / "runbooks" / "README.md",
    _REPO_ROOT / "docs" / "sre" / "runbooks" / "README.md",
]
# SLO files whose `runbook:` references we validate.
_SLO_GLOB = "docs/sre/slo/*.yaml"

_MD_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_RUNBOOK_REF = re.compile(r"^\s*runbook:\s*(\S+)\s*$")
_EXTERNAL = re.compile(r"^(https?:|mailto:|#)")


def _check_markdown_links(index: Path) -> list[str]:
    if not index.exists():
        return [f"{index.relative_to(_REPO_ROOT)}: index file not found"]
    findings: list[str] = []
    rel = index.relative_to(_REPO_ROOT)
    for line_no, raw in enumerate(index.read_text(encoding="utf-8").splitlines(), start=1):
        for target in _MD_LINK.findall(raw):
            target = target.strip()
            if _EXTERNAL.match(target):
                continue
            # strip any in-page anchor (file.md#heading -> file.md)
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (index.parent / path_part).resolve()
            if not resolved.exists():
                findings.append(f"{rel}:{line_no}: dangling runbook link -> {target}")
    return findings


def _check_slo_runbook_refs() -> list[str]:
    findings: list[str] = []
    for slo in sorted(_REPO_ROOT.glob(_SLO_GLOB)):
        rel = slo.relative_to(_REPO_ROOT)
        for line_no, raw in enumerate(slo.read_text(encoding="utf-8").splitlines(), start=1):
            m = _RUNBOOK_REF.match(raw)
            if not m:
                continue
            target = m.group(1)
            if _EXTERNAL.match(target):
                continue
            resolved = (_REPO_ROOT / target).resolve()
            if not resolved.exists():
                findings.append(f"{rel}:{line_no}: runbook path does not exist -> {target}")
    return findings


def main(argv: list[str] | None = None) -> int:
    findings: list[str] = []
    for index in _INDEX_FILES:
        findings.extend(_check_markdown_links(index))
    findings.extend(_check_slo_runbook_refs())

    if findings:
        print("Dangling runbook reference(s) found:", file=sys.stderr)
        for f in findings:
            print(f"  - {f}", file=sys.stderr)
        print(
            "\nFix the link, create the missing runbook, or update the reference to the canonical "
            "path (docs/runbooks/ for RB-NNN, docs/sre/runbooks/ for RB-SRE-NNN).",
            file=sys.stderr,
        )
        return 1
    print("OK — all runbook references resolve.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
