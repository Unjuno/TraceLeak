# Level 7 Readiness Review

Current status: Level 6 profile schema, validator, profile-to-adapter bridge, profile demo chain, and profile Markdown report have been implemented. Local validation is pending.

## What Level 6 enables

Level 6 enables a metadata-only ingress boundary for future OpenSSL-derived metadata records. The accepted input is a versioned profile object with conservative required fields, optional safe metadata fields, label-balance checks, stable run identifiers, and recursive forbidden-field rejection.

The implemented path is:

```text
profile input
  -> profile validation
  -> adapter input
  -> model-sequence sample
  -> baseline result
  -> NN result
  -> summary/report
```

## Accepted profile shape

The accepted profile input has:

- `format = traceleak.openssl_derived_metadata_profile.v1`
- `phase = P96`
- `target_decision = constant_time_helper_misuse_path`
- `metadata_only = true`
- `payload_free = true`
- `public_safe = true`
- `label_name`
- `source_pin_digest`
- `records`

Each record requires:

- `run_id`
- `source_region_token`
- `transition_token`
- `label`

Optional safe record fields are:

- `function_token`
- `module_token`
- `operation_family`
- `observation_class`
- `metadata_tags`

## Forbidden input categories

The Level 6 profile validator rejects these recursively:

- source text
- diff text
- command text
- build output
- execution output
- raw capture
- raw payload
- private key fields
- secret fields
- raw value fields
- memory dump fields
- trace byte fields
- stdout/stderr fields

## Adapter bridge behavior

The profile bridge emits the existing adapter input shape:

```text
traceleak.openssl_derived_metadata_input.v1
```

It preserves only the profile fields required by the existing adapter:

- source pin digest
- target decision
- label name
- run IDs
- source-region tokens
- transition tokens
- labels

It does not add raw payloads, source text, command text, private material, or execution output.

## Model proof

The Level 6 profile demo chain proves the following local path:

- profile input validates
- bridge output validates
- adapter emits `traceleak.model_sequence.v1`
- baseline output is generated
- NN output is generated
- profile demo summary is generated
- profile Markdown report is generated

## Still forbidden after Level 6

Do not enter Level 7 automatically. The following remain outside Level 6:

- OpenSSL build
- OpenSSL execution
- source patching
- raw trace capture
- runtime payload ingestion
- vulnerability claims

## Minimal safe next step for Level 7

Before any runtime proximity work, add a Level 7 review gate that checks:

- what local artifact will be accepted,
- who reviewed it,
- which fields are still forbidden,
- whether the artifact is metadata-only,
- whether the artifact can be processed without reading raw source, commands, private material, or execution output,
- whether the output remains a candidate-ranking or research artifact rather than a vulnerability claim.
