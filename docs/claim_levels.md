# Claim Levels

TraceLeak claim levels constrain how strongly a result may be described.

They do not prove cryptographic security. They define evidence requirements for public-safe TraceLeak reports.

## Levels

| Level | Meaning | Required Evidence |
|---|---|---|
| L0 | Tooling sanity check only | none |
| L1 | Synthetic known-signal localization | attribution report |
| L2 | Toy target localization | target evidence and attribution report |
| L3 | Local implementation observation | implementation observation and attribution report |
| L4 | Stability evidence | repeated-run or cross-build stability |
| L5 | Patch verification evidence | reduced patch verification and reduced stability |

## L5 Requirement

A public-safe L5 claim requires:

- `evidence.patch_verification.status == "reduced"`;
- `evidence.stability.status == "reduced"`;
- public-safe view;
- no raw traces;
- no secret-equivalent data.

## Validate

```bash
python scripts/validate_claim.py examples/synthetic/claim_l5_sample.json
```

JSON summary:

```bash
python scripts/validate_claim.py --json examples/synthetic/claim_l5_sample.json
```

## Example L5 Claim

```json
{
  "claim_id": "synthetic_claim_l5_0001",
  "level": "L5",
  "target": "synthetic-leak",
  "view": "redacted",
  "metric": "DeltaH",
  "evidence": {
    "patch_verification": {
      "verification_id": "synthetic_patch_0001",
      "status": "reduced"
    },
    "stability": {
      "stability_id": "synthetic_stability_0001",
      "status": "reduced"
    }
  },
  "safety": {
    "public_safe": true,
    "contains_raw_trace": false,
    "contains_secret_equivalent": false
  }
}
```

## Public-Safe Boundary

Claim files must not include:

- raw traces;
- private keys;
- random generator state;
- memory dumps;
- raw candidate values;
- secret-equivalent fields.

Claim files may include:

- report paths;
- evidence identifiers;
- public-safe scores;
- redacted summaries;
- status values;
- notes.
