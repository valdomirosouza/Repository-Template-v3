# Release Evidence Package

> **Owner:** Release Manager + SRE Lead | **Related:** [`../process/DEFINITION_OF_RELEASE.md`](../process/DEFINITION_OF_RELEASE.md) · [`../change-log/SCHEMA.md`](../change-log/SCHEMA.md) · ADR-0056 (release hardening) · ADR-0027 (ISO 27001 CM)

The auditable bundle every production release must produce. It is the evidence an auditor (ISO 27001,
SOX, SOC 2) or an incident reviewer needs to answer _what shipped, was it verified, who approved it,
and can we trace + roll it back_. Most of it is captured automatically by `cd-production.yml`; this
page is the canonical checklist + index.

---

## 1. Required artifacts

| Evidence                                                                                    | Source / where it lives                                                       | Gate                                           |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------------------------- |
| **Change record** (timestamp, deployer, service, version, commit SHA, change_type, outcome) | `docs/change-log/<date>.yaml` (append-only; schema in `change-log/SCHEMA.md`) | `cd-production.yml` → _record-change-evidence_ |
| **Immutable image digest** (`sha256:…`)                                                     | change-log `image_digest`; resolved + cosign-verified                         | `verify-artifact` (blocking)                   |
| **SBOM** (CycloneDX) + hash                                                                 | cosign attestation; change-log `sbom_hash`                                    | DoR-Release §Security                          |
| **Signature + SLSA provenance**                                                             | cosign keyless verification                                                   | `verify-artifact` (blocking)                   |
| **DAST report** (OWASP ZAP full scan)                                                       | linked in the release PR; staging attestation                                 | DoR-Release §Test Gates                        |
| **CAB approval / RFC** (`RFC_ID`)                                                           | release commit message; `change-log.rfc_id`                                   | `cab-check` (normal/emergency)                 |
| **DORA lead-time provenance**                                                               | change-log `lead_time_source`                                                 | `emit-dora-event`                              |
| **SLO / canary sign-off**                                                                   | canary burn-rate gate result (per-service SLO, ADR-0073)                      | promotion sequence                             |
| **Release notes / CHANGELOG**                                                               | release-please from Conventional-Commit titles                                | DoR-Release §Release Notes                     |
| **Rollback plan**                                                                           | RB-001 (`docs/runbooks/rollback-procedure.md`) + tested in staging            | DoR-Release §Operational                       |

## 2. How it is assembled

The package is **mostly automatic**: `cd-production.yml` verifies the artifact (digest, signature,
SBOM, SLSA), runs the CAB check, gates on the per-service SLO during canary, emits the DORA event,
and appends the change record to `docs/change-log/<date>.yaml`. The Release Manager's job is to
confirm completeness against §1 and link the human-reviewed items (DAST report, RFC) in the release
PR before promotion.

## 3. Retention & traceability

- Change-log entries are **append-only** (ISO 27001 / SOX change record); retain ≥ 7 years for
  financial-data paths (ADR-0026).
- Every entry is traceable: `commit_sha` → PR → Issue → spec/ADR (the traceability chain enforced by
  `scripts/governance/check_traceability.py`).
- A release with any §1 item missing is **not** production-ready (DoR-Release fails).

## 4. Per-release checklist (paste into the release PR)

```markdown
### Release Evidence — v<version>

- [ ] Change record appended (docs/change-log/<date>.yaml)
- [ ] Image digest cosign-verified (sha256:…)
- [ ] SBOM attested + hash recorded
- [ ] SLSA provenance verified
- [ ] DAST (ZAP) report linked
- [ ] CAB/RFC: RFC-\_\_\_\_ (normal/emergency) or standard-change
- [ ] Canary SLO sign-off (per-service thresholds)
- [ ] Release notes generated
- [ ] Rollback tested in staging (RB-001)
```
