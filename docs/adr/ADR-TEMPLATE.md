<!--
  ADR template — copy to docs/adr/ADR-NNNN-<slug>.md, fill in, and add a row to the
  Master Index in docs/adr/README.md. Keep the section skeleton; if a section does not
  apply, write "N/A — <reason>" rather than deleting it.

  Lifecycle (docs/adr/README.md): Proposed → Accepted → Deprecated → Superseded.
  ADRs are BINDING once Accepted — change a decision by filing a NEW ADR, never by
  editing an Accepted one (except to flip Status to Superseded/Deprecated with a link).
  Review before merge against docs/adr/adr-review-checklist.md.
-->

# ADR-NNNN — {Title}

**Status:** Proposed | Accepted | Deprecated | Superseded by [ADR-MMMM](ADR-MMMM-...md)
**Date:** YYYY-MM-DD
**Authors:** {name(s)}
**Deciders:** {roles who approved — e.g. Tech Lead, Security Lead}
**Review-by:** YYYY-MM-DD or `permanent` _(required for `Proposed`/temporary decisions; the date this
decision must be revisited or it auto-escalates to review)_
**Supersedes:** {ADR-XXXX, or "none"}
**Superseded-by:** {ADR-YYYY once replaced, or "—"}

---

## Context

What situation or problem prompted this decision? What constraints apply (technical, regulatory,
cost, time)? Ground every factual claim (CLAUDE.md §3.6) — link the spec, code, or source; mark
anything unverified as `uncertain — verify`.

## Decision

State clearly and unambiguously what was decided. One paragraph; an implementer should be able to act
on it without interpretation.

## Consequences

### Positive

What this decision enables.

### Negative / Trade-offs

What it costs or constrains. Each significant trade-off should be traceable to a risk in the table
below.

### Consequence tracking

> Update this table as the decision plays out — ADRs are living evidence, not write-once. A
> consequence that turned out wrong is a signal to file a superseding ADR.

| Date         | Observed consequence     | Expected?  | Action                        |
| ------------ | ------------------------ | ---------- | ----------------------------- |
| _YYYY-MM-DD_ | _what actually happened_ | _yes / no_ | _none / mitigation / new ADR_ |

## Alternatives Considered

| Alternative | Why rejected |
| ----------- | ------------ |
| _Option B_  | _…_          |

## Scope & Risk Mapping

> Makes the decision traceable (Wave 1 traceability theme). Fill what applies.

- **Affects services** _(names from `services.yaml`)_: {e.g. api-gateway, golden-signals}
- **Related specs:** {specs/...}
- **Supersession chain:** {ADR-XXXX → this → (future)}

| Risk introduced / addressed    | Likelihood | Impact  | Mitigation / control   | Owner       |
| ------------------------------ | ---------- | ------- | ---------------------- | ----------- |
| _e.g. new external dependency_ | _L/M/H_    | _L/M/H_ | _SCA gate, pin + SBOM_ | _Tech Lead_ |

## References

- {Specs, prior ADRs, RFCs, external sources.}
