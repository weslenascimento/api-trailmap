# Security and sensitive data

API Trailmap is in specification phase. No executable release or security support window has been published.

Do not include credentials, access/refresh tokens, private contracts, customer records, or unsanitized response dumps in issues, pull requests, examples, or generated artifacts.

## Report a vulnerability

Once a public repository is available, use GitHub's private vulnerability reporting if the maintainer has enabled it. If a private reporting channel is unavailable, request a private contact from the maintainer without disclosing technical exploit details publicly. A dedicated reporting contact must be configured before the first executable release.

A useful private report identifies the affected version or commit, prerequisites, impact, minimal sanitized reproduction, and any mitigation. Do not test against systems you are not authorized to access.

## Implementation security requirements

The [specification](docs/SPECIFICATION.md) requires bounded source traversal, explicit API execution scope, secret-free exports, inert rendering of remote content, and offline HTML behavior. These are requirements to validate, not claims of completed security review.
