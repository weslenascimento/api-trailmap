# Publication and brand checklist

This document tracks publication readiness without presenting pending implementation as a working release.

## Identity

- Public name: **API Trailmap**.
- Repository/skill identifier: `api-trailmap`.
- Tagline: **APIs Discovered. Paths Mapped.**
- Description: Explore APIs, map endpoint relationships, and generate agent-ready documentation and Postman collections.
- Official skill logo: supplied by the project owner at https://i.postimg.cc/PJLhtptR/logo-api-trailmap.png and bundled unchanged at `assets/brand/api-trailmap-logo.png`.

## Logo integration

The supplied artwork is saved at `assets/brand/api-trailmap-logo.png`, visually verified, and displayed in the README using a centered relative image. Alternative text: “API Trailmap — multicolor map pin combining a connected route, circuitry, and API documentation.”

Do not add a broken image reference, recreate the logo without instruction, or imply the asset has already been bundled. Confirm redistribution rights and asset licensing before public release. Derive social preview crops from the original only after checking legibility; do not distort the artwork.

## Before publishing the specification repository

- [x] Confirm repository: https://github.com/weslenascimento/api-trailmap, owned by `weslenascimento`. Name collisions have not been assessed.
- [ ] Add author attribution and a LinkedIn link if the owner wishes.
- [ ] Select a license and add the exact license text with correct attribution.
- [x] Save and integrate the supplied official logo.
- [ ] Keep the specification-phase notice visible.
- [ ] Review repository contents for secrets, personal information, and unrelated workspace files.
- [ ] Configure Issues, contribution entry points, and private vulnerability reporting as applicable.
- [ ] Set the repository description, topics, and social preview image.

Suggested topics: `api-documentation`, `agent-skills`, `api-discovery`, `postman`, `api-integration`, `developer-tools`.

## Before announcing a working release

- [ ] Implement and validate the approved requirements.
- [ ] Add exact installation and execution instructions for verified hosts.
- [ ] Publish a sanitized example with source scope and coverage.
- [ ] Validate collections and distinguish static, runtime, and live checks.
- [ ] Verify the HTML viewer with network disabled and keyboard navigation.
- [ ] Publish supported contract versions, known limitations, dependency notices, and release notes.
- [ ] Replace planning badges and roadmap entries only when evidence supports the change.

## LinkedIn launch guidance

A specification-stage announcement should invite feedback on the design and describe implementation as upcoming. A working-release announcement should link to the actual repository, show a real sanitized artifact, explain the integration problem, and state the tested limits. Do not claim exhaustive API discovery, agent compatibility, or one-click execution before demonstrating them.
