# Sales Enablement — {Product / Feature Name}

> Copy into `docs/gtm/.../sales-enablement.md` and fill in. Add the Agent-Disclosure Header if agent-drafted.
> **Reviewer:** Product Owner / Sales | **Status:** Hypothesis until field-tested.

What the team needs to explain, demo, and defend the product — whether "selling" externally or
championing internal adoption. Keep claims grounded; never invent a customer result or benchmark
(CLAUDE.md §3.6).

---

## 1. Elevator pitch (30 seconds)

> _Two or three sentences a non-expert can repeat. Lead with the problem and the differentiated value._

## 2. Qualifying questions

> Questions that reveal whether a prospect/team is a good fit (maps to the ICP).

- _Do you have AI agents taking actions with real-world effects?_
- _Do you need human accountability + audit trails for those actions?_
- _Are you under LGPD/GDPR or similar obligations?_

## 3. Discovery → value mapping

| If they say…                       | Point to…                                   |
| ---------------------------------- | ------------------------------------------- |
| _"agents move too fast to govern"_ | _two-tier HITL + autonomy feature flags_    |
| _"audits are painful"_             | _immutable audit log + traceability matrix_ |

## 4. Objection handling

| Objection                    | Response (honest, evidence-based)                                       |
| ---------------------------- | ----------------------------------------------------------------------- |
| _"Won't HITL slow us down?"_ | _autonomy is tiered; low-risk actions run autonomously, high-risk gate_ |
| _"Is this just a template?"_ | _enforced gates + runnable golden path, not just docs_                  |
| _"Lock-in?"_                 | _open structure, standard tools (OTel, OpenAPI, AsyncAPI)_              |

## 5. Demo script (golden path)

1. _Clone + `make setup-minimal`_
2. _`make run`, show `/docs`_
3. _Submit a request → show it route to HITL_
4. _Approve in the operator UI → show the audit record_
5. _Show a guardrail blocking an unsafe action_

> Keep the demo to the real, working golden path. Do not script steps that don't yet work.

## 6. FAQ

| Question                       | Answer                                                        |
| ------------------------------ | ------------------------------------------------------------- |
| _What does it cost?_           | _link `gtm-brief.md` pricing hypothesis (mark as hypothesis)_ |
| _What's the security posture?_ | _link SECURITY.md / control matrices_                         |
| _How is AI governed?_          | _link `docs/ai-governance/`_                                  |

## 7. Proof points

> Only verifiable claims: shipped capabilities, passing gates, compliance mappings. Customer
> outcomes go here **only when real** — otherwise `uncertain — verify`.
