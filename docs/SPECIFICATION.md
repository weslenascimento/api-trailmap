# API Trailmap — Implementation Specification

Status: approved product scope; implementation pending. Date: 2026-11-06.

This document is self-contained and consolidates the approved planning decisions. Technical proposals below are identified separately from confirmed product requirements. No generated collection, viewer, crawler, or executable skill is delivered by this specification.

## 1. Purpose and boundaries

Build a reusable community agent skill named `api-trailmap`. Given an API URL, it investigates accessible sources and optionally authorized live operations, produces a traceable operation inventory, maps relationships, and generates an integration handoff for developers and agents.

Repository documentation and skill instructions are English. The conversation and generated API documentation follow the user's chosen language. Preserve source field names and API literals in their original form.

Complete means all discovered operations are accounted for within the recorded scope. It does not mean every operation that exists on a provider's infrastructure has been discovered. Private, undocumented, or inaccessible surfaces remain explicit limitations.

Out of scope for this initial specification: automatic API implementation, hosted viewer services, executing API calls from the viewer, brute-force route discovery, and unrequested load/security testing. Additional protocols beyond HTTP API operations require a separate support decision; never represent unsupported sources as successfully covered.

## 2. Confirmed decisions

| ID | Decision | Reason and impact |
| --- | --- | --- |
| D01 | Name: API Trailmap; identifier: `api-trailmap`. | Shared identity for repository and skill. |
| D02 | User chooses documentation, validation, practical exploration, or a scoped mixture. | Execution is optional and tied to explicit boundaries. |
| D03 | Always generate `INDEX.md`. | Entry point remains consistent for every handoff. |
| D04 | Offer general, category, or endpoint organization. | Adapt detail to API structure; category option requires defined categories. |
| D05 | Ask whether to generate Postman exports. | Avoid unrequested files. |
| D06 | If Postman is selected, ask separately about variables and scripts. | Configuration and automation are independent choices. |
| D07 | Postman collection uses categories and separate environment files. | Supports navigation and environment configuration. |
| D08 | Continue accessible work and report missing/conflicting evidence. | Partial access must not erase useful findings or produce fabricated completeness. |
| D09 | Ask when an essential flow cannot be established. | Missing authentication or essential contract details must not be invented. |
| D10 | Optional versioned structured JSON export. | Allows downstream processing of fields, operations, and relationships. |
| D11 | Optional standalone HTML/JavaScript viewer with embedded data. | Opens locally, without server or external runtime dependencies. |
| D12 | Viewer includes search, filters, graph navigation, structures, details, and evidence. | Makes both workflow and payload exploration possible. |
| D13 | Documentation and exports distinguish evidence and execution coverage. | Agents can assess uncertainty and act accordingly. |
| D14 | Real credentials and tokens are excluded from delivered artifacts. | Export templates remain shareable. |

## 3. User journey and intake

### 3.1 Intake

Recover all preferences and permissions already stated. Ask only unresolved choices, in small related groups. Never require the user to repeat a decision.

Collect the initial URL, output language, exploration mode, Markdown organization, Postman selection, Postman variable/script selections when applicable, JSON selection, and HTML selection.

When executing operations, establish target environment, allowed hosts, operations or categories, permitted side effects, request/time budget, and stop conditions. Use existing session authorization when sufficient. Do not require execution details for documentation-only work.

If the user selects category organization before categories are known, inspect sources first and then explain the available grouping. Do not silently invent official categories. A proposed grouping can be offered as a labeled generated organization.

### 3.2 Discovery

Identify whether the URL is documentation, a machine-readable contract, or an API base URL. Follow relevant in-scope navigation, linked contract files, pagination in documentation, and references. Maintain a visited-source inventory and record inaccessible, unsupported, or excluded sources.

Resolve relative references against the correct source URI. Prevent infinite reference traversal. Preserve recursive schema references as references. Do not flatten away content types, alternatives, nullability, read/write distinctions, or request-versus-response requiredness.

Identify declared servers, versions, categories, authentication, operations, and deprecation notices. Different methods on one path are different operations. Deduplicate repeated descriptions of the same operation while preserving evidence and conflicts. A base URL alone is not evidence for guessing route names.

Discovering additional hosts does not automatically authorize live requests to them. Documentation acquisition and API execution are tracked separately.

### 3.3 Execution, when selected

Run only permitted operations against the agreed environment. GET or a read-looking name alone does not establish absence of side effects. Before a flow, verify prerequisites and authorized mutations.

Record operation, environment, time, sanitized inputs, status, relevant headers, sanitized response evidence, and outcome. Never persist authorization headers or raw secret-bearing responses. Do not treat a sample response as a complete schema.

Stop or pause the dependent flow for revoked access, ambiguous essential credentials, unapproved mutations, rate limits beyond the agreed policy, repeated authentication failure, or exhausted budget. Continue unrelated authorized analysis where useful. Preserve partial results and explain the boundary.

### 3.4 Handoff

Generate only requested outputs, validate their consistency, and report artifact paths, inventory counts, execution coverage, exclusions, and unresolved questions. Do not describe unexecuted scripts as verified against the API.

## 4. Domain concepts and ownership

Use a small canonical inventory shared by all renderers. Proposed domain concepts:

- **Investigation:** selected scope, preferences, sources, permissions, coverage, and resulting inventory.
- **Source:** an identifiable document or sanitized observation with location and retrieval context.
- **Operation:** stable identity for a method/path within a server/version context.
- **Schema definition:** reusable request or response structure, including recursive references.
- **Relationship:** explicit connection between operations or data fields.
- **Evidence:** support for a claim, including documented or observed facts and inference rationale.
- **Artifact:** a selected generated output and its validation outcome.

Keep acquisition, normalization, inference, rendering, and validation separate. Renderers consume the same inventory; they must not independently invent facts. Do not create domain aggregates or persistence services unless implementation needs justify them.

## 5. Functional requirements

| ID | Requirement | Acceptance criterion |
| --- | --- | --- |
| FR01 | Accept an API URL and inspect accessible sources. | Each accessed, blocked, excluded, or unsupported source has a recorded disposition. |
| FR02 | Inventory operations. | Every discovered method/path/server/version identity has one stable record. |
| FR03 | Capture operation contracts. | Parameters, headers, body, responses, and authentication are represented or explicitly unknown. |
| FR04 | Preserve field semantics. | Nested fields, types, requiredness, constraints, and references survive normalization. |
| FR05 | Map relationships. | Each edge resolves to existing operations/fields and carries type, evidence, and certainty. |
| FR06 | Generate complete Markdown handoff. | `INDEX.md` provides context, navigation, maps, setup, coverage, and gaps without relying on chat history. |
| FR07 | Support all three organization modes. | The selected mode accounts for every discovered operation or justified exclusion. |
| FR08 | Generate optional Postman exports. | Files parse, collections validate against the selected format, and required configuration is explained. |
| FR09 | Respect variable/script selections. | No omitted option is silently added; consequences of missing configuration are documented. |
| FR10 | Generate optional JSON. | Export declares a schema version, validates against its published schema, and contains no dangling references. |
| FR11 | Generate optional HTML. | A single file opens over `file://` with network disabled and exposes all selected inventory records. |
| FR12 | Provide search and filters. | Paths, methods, categories, and field names are searchable; combined category/method filters behave consistently. |
| FR13 | Preserve uncertainty. | Official examples, illustrative examples, documented facts, observations, inferences, and conflicts are distinguishable. |
| FR14 | Report coverage. | Counts are reproducible from inventory dispositions and distinguish documentation from execution. |
| FR15 | Keep sensitive values out of artifacts. | Fixtures with tokens and personal data produce sanitized exports and embedded viewer data. |

## 6. Canonical data contract

The following is a proposed logical model, not an implemented JSON schema. The implementation must publish a concrete versioned schema and migration policy before export stability is promised.

| Record | Required information |
| --- | --- |
| Root | `schemaVersion`, generation time, API identity, scope, language, preferences, sources, operations, schemas, relationships, coverage, gaps. |
| Source | Stable ID, source kind, sanitized locator, retrieval time, accessibility, relevant section or pointer. |
| Operation | Stable ID, method, path, server/version references, category references, purpose, authentication, parameters, request bodies, responses, evidence references, disposition. |
| Field/schema | Stable reference or pointer, name, location, type representation, requiredness, constraints, child/reference definitions, examples, evidence. |
| Authentication | Scheme, placement, required scopes, prerequisite operation when established, and missing setup values. |
| Relationship | ID, producer, consumer, kind, source selector, target binding, evidence references, certainty, explanation. |
| Gap/conflict | Affected record, missing or conflicting claim, sources, operational impact, question or resolution status. |
| Observation | Operation reference, environment label, timestamp, sanitized evidence, outcome, limitations. |

Unknown values must not be encoded as false or empty success. The schema must distinguish unknown, absent, optional, and explicitly null values where these differ. Use stable IDs, not array positions, for cross-record links.

Proposed relationship kinds: authentication prerequisite, value propagation, execution prerequisite, and documented resource association. A resource association is not automatically an execution-order constraint. Matching field names alone cannot establish a confirmed dependency. Record cycles and conditional paths; do not force every API into a linear chain.

For value propagation, identify the response selector that produces a value and the path/query/header/body target that consumes it. Validate both against known structures where possible. Runtime values belong in local execution state, not the shared inventory export.

Evidence should attach to individual claims when facts within one operation have different support. Documented and observed are independent provenance dimensions; disagreement is preserved rather than overwritten.

## 7. Markdown contract

Always generate `INDEX.md` with:

1. API purpose, scope, language, generation context, and source list.
2. Instructions for a receiving developer or agent, including recommended reading order.
3. Base URLs, environments, authentication setup, and configuration placeholders.
4. Inventory with links to operation details.
5. Mermaid workflow/dependency maps and a text explanation independent of diagram rendering.
6. Confirmed workflows with prerequisites, value propagation, side effects, and failure handling.
7. Relevant API-wide pagination, limits, errors, and retry/idempotency guidance only when supported.
8. Output import/use instructions, including Postman script behavior when selected.
9. Coverage dimensions, conflicts, inaccessible areas, exclusions, and outstanding questions.

Operation details include method/path, purpose, category, authentication/scopes, parameters, headers, content types, request/response fields, status codes, errors, examples, dependencies, evidence, and execution disposition. Label unavailable sections explicitly. Do not fabricate error codes, retry rules, business requirements, or response payloads.

Use deterministic collision-safe filenames and relative links. General mode keeps the complete reference in `INDEX.md`; other modes link to detail files without losing shared context. Do not claim the reference fits every agent's context window; guide selective loading for large APIs.

## 8. Postman contract

Proposed initial target: Postman Collection v2.1, subject to implementation validation. Group operations by source category. Where no source category exists, clearly identify any generated fallback grouping. Keep environment files separate; create only requested environments.

With variables enabled, use consistent names and scopes for base URLs, configuration, credentials, tokens, and captured IDs. Delivered sensitive values are empty. Mark essential empty configuration and explain how to supply it locally. Environment labels do not prove endpoint safety.

With scripts enabled, generate only evidence-supported behavior. Token acquisition, refresh, response selectors, expiry, and authentication placement must come from identified sources or authorized observations. Prevent retry or refresh loops. On authentication failure, avoid reusing a stale captured token. Captured values require response-status and shape checks before assignment.

If scripts are selected without variables, explain when durable token/ID propagation requires variables and ask for the narrow missing choice; do not silently override the preference. Without variables, do not emit unresolved template placeholders as if the collection were configured. Document literal configuration steps and leave secrets blank.

If variables are selected without scripts, provide manual token/ID setup instructions. A valid authentication flow that cannot be automated remains documented and explicitly manual.

Post-response assertions verify only known properties. A failed request must not populate downstream values or be reported as success. Request ordering must reflect confirmed prerequisites and conditional paths. Mutating requests need visible side-effect descriptions and must not run implicitly as setup when unauthorized.

Validate JSON parsing, collection schema, environment structure, defined variable references, script syntax, selector references, and correspondence to the canonical inventory. Static validation is distinct from Postman runtime validation and live API validation; report each separately.

## 9. HTML viewer contract

One HTML file contains embedded styles, JavaScript, and a sanitized inventory. No external fonts, CDNs, network requests, server, or runtime installation are required. Bundle any chosen library locally inside the artifact and comply with its license; no graph library is selected by this specification.

Provide an API relationship map and an expandable data-structure view. Support pan, zoom, node expansion, selection, and details. Edge labels identify the dependency kind and propagated value. Visually distinguish inferred edges without relying solely on color.

Search is case-insensitive and includes operation path, HTTP method, category name, and nested field name. Results identify the containing operation and can navigate to its details. Category/method filters combine consistently, show visible/total counts, and provide a clear reset action. If filtering hides a dependency endpoint, indicate the hidden connection instead of implying the dependency does not exist.

Show empty, no-results, incomplete-data, and conflicting-evidence states. Long labels and large payloads must remain readable. Use progressive expansion for large inventories; determine a benchmark and publish measured limits before claiming scale support.

Provide keyboard-accessible search, filters, result navigation, details, visible focus, and a list-based alternative to graph navigation. Include appropriate labels and sufficient contrast. The output language controls UI labels without changing source identifiers.

Treat all source text as untrusted. Use text-safe rendering, safe URL schemes, and robust embedded-data escaping, including strings containing `</script>`. Never evaluate source-provided strings as code. The viewer must not invoke API operations, contain credentials, or require remote content to open.

## 10. Coverage and stop conditions

Use independent counts for discovered, documented, executed, blocked, and excluded operations. Define each count and denominator. Maintain an explicit disposition for each discovered operation; document partial records instead of dropping them. Track source accessibility separately from operation execution outcomes.

Bound traversal by visited-source tracking, approved hosts, pagination, time/request limits, and explicit exclusions. Defaults are an implementation proposal to be documented, not hidden product behavior. Report the chosen boundary in the handoff.

Authentication, unsupported contract versions, unresolved essential references, and exhausted budgets produce partial completion with actionable gaps. They do not justify invented contracts or an unqualified complete result.

## 11. Acceptance scenarios

| ID | Scenario | Expected observable result |
| --- | --- | --- |
| AT01 | Documentation-only input with linked contract. | Sources are retrieved; no API operation is invoked; inventory references source evidence. |
| AT02 | User already supplies all preferences. | No repeated intake; requested artifacts only. |
| AT03 | Source includes GET and POST on the same path. | Two distinct operation records and matching output entries. |
| AT04 | Categories are absent. | No fabricated official categories; grouping choice is explained. |
| AT05 | Authentication documentation omits the token selector. | Missing detail is recorded; no fabricated extraction script is delivered as working. |
| AT06 | Authorized login returns a documented token shape. | Optional script checks success and shape, captures the configured value, and fails clearly without leaking it. |
| AT07 | Same field name appears in unrelated resources. | No confirmed dependency based only on the name. |
| AT08 | Sources disagree on a response field. | Both sources and the conflict remain visible across selected outputs. |
| AT09 | User selects HTML and declines separate JSON. | Self-contained HTML works offline; no JSON export is generated. |
| AT10 | Search matches a deeply nested attribute. | Results lead to its containing operation and field details. |
| AT11 | Source contains HTML/script-like strings. | Viewer renders inert text and runs no injected code. |
| AT12 | API response includes token and personal information. | Generated examples, inventory, logs, and HTML do not expose those values. |
| AT13 | Scope is read-only and workflow needs a POST mutation. | Mutation is not executed without matching authorization; dependent flow is explained as blocked. |
| AT14 | Contract references itself recursively. | Traversal terminates; schema reference is preserved and viewer expansion remains usable. |
| AT15 | Filter hides a producer operation. | Hidden dependency is disclosed; relationship semantics remain accurate. |
| AT16 | Rate limit or budget stops exploration. | Partial artifacts and coverage report identify the stop boundary. |
| AT17 | Any selected output omits an inventoried operation. | Validation fails unless a recorded exclusion explains the omission. |
| AT18 | Keyboard-only user explores the viewer. | Search, filters, results, and details remain usable without graph gestures. |

## 12. Implementation sequence and quality gates

1. Implement the skill entry point and focused references from this specification. Validate the skill structure and preserve platform portability; avoid host-specific absolute paths.
2. Define the canonical schema and synthetic fixtures covering authentication, schemas, cycles, missing evidence, and conflicts.
3. Implement source acquisition and normalization with bounded traversal and evidence references.
4. Implement Markdown rendering and verify all selected organization modes.
5. Implement Postman export with static checks and isolated runtime validation where feasible.
6. Implement optional JSON and HTML rendering from the shared inventory.
7. Exercise acceptance scenarios and deliver a real, sanitized example package before advertising a working release.

Use deterministic helpers for repeated parsing, validation, and rendering where they improve reliability. Keep `SKILL.md` focused on workflow and decision rules; put format-specific detail in references. Avoid generating a large skill scaffold without a concrete use for each file.

Check meaningful invariants: inventory/output correspondence, schema fidelity, edge resolution, secret exclusion, independent option behavior, and offline viewer operation. Report which validations ran and which require unavailable access. Do not execute against production solely to demonstrate project readiness.

## 13. Publication decisions still open

- Confirmed repository: https://github.com/weslenascimento/api-trailmap, owned by `weslenascimento`. Author display attribution and LinkedIn profile link remain open.
- License for code, documentation, and supplied branding assets.
- Logo placement is complete: `assets/brand/api-trailmap-logo.png`, displayed with alternative text in the README. Future skill packaging must include the official asset when needed.
- Runtime/toolchain, supported source/contract versions, schema version policy, and dependency licenses.
- First release version, measured viewer capacity, and verified agent host compatibility.

These do not change approved product behavior. Implementation may propose technical choices, but public claims must reflect actual verified support.

## 14. Repository-link installation requirement

The user must be able to ask a compatible agent to install API Trailmap from https://github.com/weslenascimento/api-trailmap. The installable distribution must contain `SKILL.md` and all required references, scripts, and assets. Document supported host destinations, prerequisites, version selection, updates, and verification. Installation must preserve unrelated skills and user configuration and must not report success until required files and dependencies are verified. State any required session reload. Repository access and filesystem installation permissions remain host prerequisites; do not promise universal installation support before testing it. The current specification-only repository does not satisfy this installation requirement yet.
