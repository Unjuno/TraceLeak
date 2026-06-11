# Local OpenSSL Instrumentation Plan

This document defines the preconditions for any local OpenSSL RSA key-generation work in TraceLeak.

OpenSSL work is intentionally local-only until the synthetic and toy RSA-like targets are validated.

## Preconditions

Before starting OpenSSL instrumentation:

- public-safe foundation tests pass;
- synthetic target workflow runs end to end;
- toy RSA-like workflow runs end to end;
- generated reports contain no raw traces or secret-equivalent material;
- local output directories are ignored by git;
- raw-to-redacted conversion rules are documented.

## Scope

Initial scope:

- local OpenSSL build only;
- local toy key sizes only;
- self-generated experimental inputs only;
- source-level instrumentation patches only;
- redacted reports only.

Out of scope:

- third-party keys;
- production traces;
- production services;
- committed raw traces;
- committed private keys;
- committed random generator state;
- model checkpoints in the public repo.

## Recommended Local Directory Layout

```text
third_party/
  openssl/               # submodule or local clone, not bundled by default
reports/local/
  openssl_rsa_keygen/    # generated reports only
runs/local/
  openssl_rsa_keygen/    # ignored local traces
patches/openssl/
  README.md
```

## Trace View Policy

| View | Public repo | Use |
|---|---:|---|
| `meta` | yes | build metadata baseline |
| `path` | yes, if safe | branch/phase/loop structure |
| `redacted` | yes, if safe | derived buckets and summaries |
| `observable` | yes, if safe | timing/perf summaries |
| `raw` | no | local upper-bound analysis only |
| `cheat` | no | positive controls only |

## Instrumentation Strategy

Start with narrow source-level probes:

1. phase events around key-generation stages;
2. path events around loops and branches;
3. redacted candidate metadata only;
4. no raw candidate values;
5. no private factors;
6. no random generator state.

## Local Workflow Sketch

```text
build local OpenSSL
  -> run local instrumented toy key generation
  -> write local raw trace
  -> convert raw trace to redacted/path view
  -> validate public-safe view
  -> extract features
  -> evaluate baselines
  -> import optional model result
  -> generate public-safe report
```

## Claim Levels

| Level | Meaning |
|---|---|
| L0 | tooling sanity check only |
| L1 | synthetic known-signal localization |
| L2 | toy RSA-like localization |
| L3 | local OpenSSL toy-key observation |
| L4 | cross-build or cross-run stability |
| L5 | before/after patch verification |

OpenSSL observations should not be presented above L3 unless stability or patch verification evidence exists.

## Public Release Rule

A public OpenSSL-related artifact must be one of:

- documentation;
- patch file without raw data;
- config template;
- redacted summary;
- generated report without secret-equivalent data.

A public OpenSSL-related artifact must not contain:

- private keys;
- raw candidate values;
- factors;
- random generator state;
- memory dumps;
- full raw traces.
