# Install API Trailmap

Ask your agent:

```text
Install the API Trailmap skill from https://github.com/weslenascimento/api-trailmap.
Read INSTALL.md, install the complete package in your supported skill directory,
and verify the installation. Do not replace an existing installation without checking it.
```

The repository root contains `SKILL.md`. There is no nested skill directory to discover. A compatible agent can clone/download this repository and place the complete package in a directory named `api-trailmap` inside its supported skill location. Preserve `SKILL.md`, `INSTALL.md`, `references/`, `scripts/`, `assets/`, `schemas/`, and `examples/` together. Runtime helpers use relative paths and Python's standard library; no pip or npm installation is required.

## Requirements

- A host that loads Agent Skills, or an agent explicitly instructed to read `SKILL.md`.
- Web/HTTP retrieval and local file access for API investigations.
- Python 3.10+ for the bundled generator. On some Windows installations use `py -3` instead of `python`.
- Git for the clone examples, or an equivalent repository archive download.

## Manual installation

For hosts supporting a project-local `.agents/skills` directory, run from the project where you will use the skill:

```text
git clone https://github.com/weslenascimento/api-trailmap.git .agents/skills/api-trailmap
python .agents/skills/api-trailmap/scripts/verify_install.py
```

For a host using another directory, clone into its documented skill location instead. Claude Code installations commonly use `.claude/skills/api-trailmap`; consult the host's current documentation before selecting a destination. Do not install duplicate copies into several discovery paths at once. A successful clone does not by itself prove a host has loaded the skill.

If a destination already exists, inspect local changes and its source before updating it. Do not delete or force-reset it. For an unchanged Git installation, `git pull --ff-only` in the skill directory updates it without rewriting history. For a pinned release or commit, preserve the user's version selection.

## Verify and use

Run `scripts/verify_install.py` from the installed package. It checks the required resources and executes an isolated generation smoke test using synthetic data. It makes no network requests and invokes no API operations. Then start a new agent session if necessary and ask the host to list or use API Trailmap. Report separately whether files are installed and whether host discovery was confirmed.

Example request:

```text
Use API Trailmap to analyze https://api.example.com/docs.
Ask me about exploration mode, Markdown organization, Postman, JSON, and HTML.
Generate the documentation in Portuguese.
```

If automatic discovery is unavailable, explicitly ask the agent to read the installed `SKILL.md` and follow it. This is a manual workflow, not verified native host integration.

## Try the generator without an API

From this repository's root:

```text
python scripts/generate.py --input examples/inventory.json --output output/demo
python -m unittest discover -s tests -v
```

Open `output/demo/INDEX.md` and `output/demo/api-trailmap.html`. The fixture is synthetic and does not represent a real service. Use a fresh output directory for each generation.

## Uninstall

Remove only the installed `api-trailmap` directory after checking it contains no user work. Do not remove the host's shared skill directory. Generated integration packages are independent and remain available.
