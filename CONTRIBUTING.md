# Contributing to API Trailmap

Thank you for helping make API integrations easier to understand. The project is currently in specification phase; read the [README](README.md) and [implementation specification](docs/SPECIFICATION.md) first.

## Propose a change

Use the repository's Issues area once the repository is published. Describe the problem, who encounters it, an expected result, and a small synthetic example. For behavior changes, identify the affected requirement or acceptance scenario. Separate current defects from proposed future support.

Before a substantial implementation, discuss its scope so that schema, rendering, and skill changes remain consistent. Small documentation corrections can be proposed directly.

## Prepare a contribution

1. Keep changes focused on a concrete problem.
2. Use English for maintained project documentation and skill instructions.
3. Preserve evidence, uncertainty, and the user's output/execution choices.
4. Use synthetic or explicitly shareable fixtures; remove secrets and personal data.
5. Explain the change, how it was validated, and any known limitations in the pull request.

There is no implemented runtime or test command yet. Do not invent passing checks. As implementation lands, each executable component must document its real setup and verification commands.

## Review expectations

Reviewers should be able to trace the change to an observable behavior. Validate affected output formats and consistency between them. Viewer contributions must consider offline behavior, keyboard access, and untrusted source data. Authentication contributions must avoid live credentials and uncontrolled side effects.

Communicate respectfully, critique the work rather than the person, and provide reproducible evidence. Do not post security findings publicly; follow [SECURITY.md](SECURITY.md).

## Licensing status

The repository license is pending. Resolve the licensing terms before accepting code contributions or third-party assets. Identify the origin and license of any proposed dependency or media file.
