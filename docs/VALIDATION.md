# Initial implementation validation

Validated locally on 2026-11-06. This records checks actually performed; it is not a certification of every agent host or API provider.

## Passed

- Skill frontmatter/name validation with the local skill-creator validator.
- Required package resource check and isolated offline generation smoke test.
- Nine Python unit tests covering Markdown organization/local links, dangling/duplicate references, optional outputs, capture evidence/preferences, secret-field redaction, overwrite protection, coverage/exclusions, embedded-data escaping, viewer JavaScript syntax, and capture-hook success/failure with a local Postman test double.
- Inventory schema validation with JSON Schema Draft 2020-12 against the synthetic fixture.
- Generated collection validation against the official Postman Collection v2.1 schema, retrieved for the check.
- Browser integration on Microsoft Edge through Playwright, opening the generated HTML using `file://` with network disabled. Verified nested contract search, category/method filters, details, hidden dependencies, zoom, keyboard focus, no JavaScript errors, and no HTTP requests.
- Visual inspection of the generated desktop viewer.

## Reproduce core checks

```text
python scripts/verify_install.py
python -m unittest discover -s tests -v
python scripts/generate.py --input examples/inventory.json --validate-only
```

Unit tests require Node.js in addition to Python. Browser integration is optional and needs Playwright and an installed Microsoft Edge browser:

```text
python scripts/generate.py --input examples/inventory.json --output output/browser-check
node tests/viewer.cjs output/browser-check/api-trailmap.html
```

Install Playwright in a development environment separately; it is not a runtime dependency of the distributed skill or viewer. An optional third argument to `tests/viewer.cjs` selects an external Playwright package path.

## Not established by these checks

- Native skill discovery in every supported agent product/version.
- End-to-end discovery of a real API or completeness of an agent-authored inventory.
- Postman application import or live Postman runtime execution.
- Live token refresh, provider-specific authorization, or mutations.
- Performance on very large inventories, mobile layout certification, or a full accessibility/security audit.

No real API operation was invoked by these validation steps. The example contains synthetic data only.
