# Security Policy

TraceLeak is a defensive research project for measuring and localizing leakage in cryptographic implementations.

It is not intended for offensive use, third-party key recovery, production exploitation, or unauthorized analysis.

## Allowed Use

TraceLeak may be used for:

- local experiments on systems you own or operate;
- self-generated toy keys;
- controlled cryptographic implementation testing;
- source-level leakage assessment;
- defensive regression testing;
- responsible vulnerability research;
- comparing raw, redacted, path-only, and observable trace views.

## Prohibited Use

Do not use TraceLeak to:

- attack systems you do not own;
- recover third-party private keys;
- analyze private keys or traces obtained from third parties;
- exfiltrate memory, RNG state, DRBG state, or private key material;
- target production cryptographic services;
- bypass access controls;
- publish raw secret-equivalent traces.

## Data Handling

Raw execution traces may contain secret-equivalent material.

Never commit:

- raw RNG output;
- DRBG internal state;
- raw prime candidates;
- RSA private factors `p` or `q`;
- private exponent `d`;
- full private keys;
- production traces;
- memory dumps;
- core dumps;
- raw traces from non-toy experiments.

Allowed in the public repository:

- code;
- documentation;
- trace schemas;
- synthetic toy traces;
- redacted examples;
- metrics;
- evaluation scripts;
- OpenSSL instrumentation patches;
- reports that do not contain secret-equivalent raw data.

## Raw Trace Policy

Raw traces are lab-only artifacts.

They may be used to estimate an upper bound on leakage, but security claims must not rely only on raw traces.

Before sharing any trace sample, convert it to a safer view:

```text
raw -> redacted
raw -> path
raw -> meta
```

The `raw` and `cheat` views must never be used as public evidence of real-world exploitability.

## Responsible Disclosure

If TraceLeak identifies a potential vulnerability in a maintained cryptographic implementation:

1. Do not publish exploit details immediately.
2. Do not open a public issue containing sensitive reproduction steps.
3. Contact the affected maintainers through their security reporting process.
4. Share only the minimum information required for triage.
5. Publish technical details only after coordination or after the issue is no longer sensitive.

## Reporting Security Issues in TraceLeak

If you find a security issue in TraceLeak itself, please report it privately to the project maintainer.

Do not include raw private keys, production traces, RNG state, or third-party secrets in reports.
