# OpenSSL Target Selection Plan

Status: P27.

This document narrows the first real OpenSSL analysis target for TraceLeak. It does not authorize OpenSSL build, instrumentation, runtime observation, patching, or payload capture. It only defines a reviewed target-selection plan that later gates can reference.

## Selection criteria

| Criterion | Meaning |
|---|---|
| Leakage-localization relevance | Whether source-level variable / transition / code-region ranking is meaningful for the target. |
| Feasibility | Whether the target can be isolated without broad OpenSSL-wide instrumentation. |
| Expected trace shape | Whether the target can produce stable model-sequence features. |
| False-positive risk | Whether observed differences are likely to be incidental metadata or build artifacts. |
| Public explanation quality | Whether a public metadata-only demo can explain why the target matters without publishing sensitive internals. |

## Candidate ranking

| Rank | Target | Rationale | Initial decision |
|---:|---|---|---|
| 1 | Constant-time helper misuse path | Best match for TraceLeak attribution: variables, branches, transitions, and helper misuse can be ranked. | Preferred first target. |
| 2 | BN modular exponentiation path | High cryptographic relevance, but more complex and higher false-positive risk. | Second target. |
| 3 | RSA private operation path | Strong security relevance, but broad and competitive. | Defer until adapter is stable. |
| 4 | EC scalar multiplication path | Important but harder to isolate and interpret. | Later target. |
| 5 | Parser / decoder path | Useful comparison target but less aligned with leakage localization. | Control / comparison target. |

## First target

The first target should be a narrow **constant-time helper misuse path**.

Expected public-safe representation:

- symbolic source-region identifiers;
- symbolic helper names or helper-family tokens;
- redacted branch / transition categories;
- no OpenSSL source text;
- no command text;
- no build output;
- no execution output;
- no raw capture;
- no runtime payload.

## Non-goals

This plan does not claim an OpenSSL vulnerability. It does not authorize publishing a concrete finding. It does not authorize real OpenSSL execution or instrumentation. Those require a later reviewed runtime transition gate.

## Next gate

P28 should encode this target-selection decision into a runtime transition gate. The gate should remain conservative until the local workspace, redaction policy, and reproducibility requirements are satisfied.
