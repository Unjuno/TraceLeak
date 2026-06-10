# Safety Boundary

TraceLeak is a defensive leakage assessment framework.

Its safety boundary is part of the design. The project must remain useful for local, controlled cryptographic implementation testing without becoming a tool for unauthorized key recovery or exploitation.

## Allowed

- Local experiments on systems owned or operated by the researcher.
- Self-generated toy keys.
- Synthetic leakage targets.
- Locally instrumented cryptographic implementations.
- Defensive source-level leakage assessment.
- Responsible vulnerability research.
- Redacted or synthetic public examples.

## Not Allowed

- Attacking systems not owned or operated by the researcher.
- Recovering third-party secrets.
- Analyzing third-party private keys.
- Exfiltrating memory, RNG state, DRBG state, or private key material.
- Targeting production cryptographic services.
- Publishing raw secret-equivalent traces.

## Secret-Equivalent Data

The following data must be treated as secret-equivalent:

- raw RNG output;
- DRBG internal state;
- raw prime candidates;
- RSA private factors `p` and `q`;
- RSA private exponent `d`;
- private keys;
- raw OpenSSL key generation traces;
- memory dumps;
- core dumps;
- production traces.

## Public Data Policy

Public examples must be one of:

- synthetic;
- redacted;
- path-only;
- metadata-only;
- explicitly marked as non-secret toy data.

Raw traces may be used locally for upper-bound experiments, but they must not be committed to the public repository.

## Claim Boundary

TraceLeak findings should be reported using claim levels:

- raw-only findings are upper-bound measurements;
- redacted/path/observable findings are stronger;
- source-localized findings are stronger still;
- patch-verified findings are the strongest.

A claim that depends only on raw secret-equivalent data must not be framed as real-world exploitability.
