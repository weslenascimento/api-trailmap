# Inventory contract — version 1.0

Use `examples/inventory.json` as a synthetic working example and `schemas/inventory.schema.json` as the public shape reference. These files are included in the installable package. The helper performs structural and semantic checks; it is not a general-purpose JSON Schema engine. Optional data not understood by a renderer is retained in JSON/HTML details and operation contract blocks.

Required root keys:

- `schemaVersion`: `1.0`.
- `api`: object with `name`, `baseUrl` (may be empty when unknown), optional `description`, `setup`, and `workflows` written in the output language.
- `language`: `en` or `pt-BR` for built-in UI labels. For another language the agent must translate generated headings/UI and revalidate; baseline helper labels fall back to English.
- `scope`: readable boundary, source limitations, and execution mode.
- `preferences`: `organization` (`general`, `category`, `endpoint`) and explicit booleans `postman`, `variables`, `scripts`, `json`, `html`.
- `sources`: records with unique `id`, `locator`, and `status`; optional notes/time.
- `operations`: records described below.
- `relationships`: records described below; empty array allowed.
- `gaps`: readable strings describing unavailable information/conflicts; empty array allowed.

Operation required keys: `id` (unique stable slug), `method`, `path`, `summary`, `category` (use `Uncategorized` only as a labeled fallback), `evidence` (source ID array), `contract` (object), `documented`, `executed`, `blocked`, `excluded` (booleans). An excluded operation also requires `exclusionReason`. Additional server/version fields preserve distinctions between operations with the same method/path. Contracts can contain arbitrary source-faithful schema objects, examples and provenance. Recommended keys: `authentication`, `parameters`, `requestBody`, `responses`, `pagination`, `limits`, `errors`, `notes`. Use null or explicit unknown descriptions where evidence is absent; do not turn unknown into false. Store execution observations and conflicts with their evidence as additional fields.

Optional Postman-specific operation fields:

- `parameters`: array of `{name, in, required, description}` for path/query/header/cookie values.
- `requestBody`: a sanitized illustrative JSON object; omitted means no generated body, not proof that no body exists. Put raw contract schemas in `contract`.
- `auth`: `{type: "bearer", variable: "access_token"}` only when supported by evidence. Other schemes remain documented for manual setup or source-specific extension.
- `captures`: array of `{variable, pointer, evidence, successCodes}`. `pointer` is an RFC 6901 response JSON pointer, such as `/access_token`; `evidence` contains supporting source IDs; `successCodes` is a nonempty list of supported success status codes. No invented selectors. Requires variables and scripts. Captured values remain runtime state, never artifact values.
- `preRequestScript` / `postResponseScript`: optional arrays of source-specific JavaScript lines reviewed by the agent. They are emitted only with scripts enabled. Record their evidence/rationale in the contract. They are trusted implementation code, not scraped source text.

Relationship required keys: unique `id`, `from` and `to` operation IDs, `kind`, `certainty` (`documented`, `observed`, `inferred`), `evidence` (source ID array), and `description`. Optional `pointer` and `target` describe produced/consumed values. Inferred edges require a rationale in `description`. An observed edge describes a scoped observation, not universal behavior.

The helper computes coverage from booleans. `documented` and `executed` are independent; blocked/excluded are separate dimensions. Unknown totals outside the discovered inventory remain unknown. Operation ID references must resolve, including excluded records. Do not use optional Postman fields to replace complete source contracts.

Generate into a new or empty directory. If generation fails, inspect/remove only partial generated artifacts in that directory before retrying. Do not overwrite a user's existing handoff. Run `--validate-only` before rendering. The JSON export and embedded HTML data are sanitized copies of the same inventory; they omit real secret values.
