# Discovery and evidence

Start with the given source, classify it, and keep a source ledger: ID, URL/file locator, retrieval time if known, status (`accessible`, `blocked`, `excluded`, or `unsupported`), and notes. Resolve references against each source URI. Track visited URIs/fragments, recursive references, cross-host links, and documentation pagination. Do not silently stop at the first page or silently expand the authorized API host scope.

Use available agent tools for dynamic documentation and linked JSON/YAML contracts. No parser bundled here claims complete OpenAPI version coverage. Preserve original schemas in inventory values rather than flattening away `oneOf`, `allOf`, `$ref`, `required`, nullable types, examples, or media types. When tools cannot parse or retrieve something, mark it unsupported/blocked and explain the impact.

Negotiate finite traversal/execution limits appropriate to the source. Stop at denied access, user boundaries, rate limits, or exhausted budgets; report partial coverage. Do not brute-force route names. A public documentation URL may describe private operations that cannot be validated.

For each operation, distinguish server/version context, HTTP method/path, documented business purpose, authentication/scopes, path/query/header/cookie inputs, bodies, responses/status codes, errors, pagination, filters, retry/idempotency constraints, and deprecation. Keep unknown fields explicit. An example does not prove requiredness, exhaustive types, or all response codes.

Relations need producer/consumer identities, type, optional response selector/target binding, source evidence, certainty, and rationale. Distinguish association from execution order. Matching `id` fields is insufficient evidence. Cyclic schemas and conditional workflows are valid.

Live execution requires agreed environment and scope. Do not infer safety from GET alone. Record sanitized observations, environment, time, status, and limitations; never retain raw authentication responses. Mutations and cleanup require matching authorization. Never auto-run a collection to validate its syntax.

The helper cannot recognize all sensitive text. Before writing an inventory, sanitize URLs, free-form descriptions, custom header names, example values, identifiers, and personal data. Keep structural names/types and use illustrative values. Evidence locators must not include credentials or signed query strings. Reconcile conflicts visibly; do not overwrite documentation with one observed response.
