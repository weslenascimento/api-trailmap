#!/usr/bin/env python3
"""Verify package resources and run an isolated, offline smoke test."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10+ is required")
    required = ["SKILL.md", "INSTALL.md", "references/discovery.md", "references/inventory.md", "references/postman.md", "scripts/generate.py", "assets/viewer.html", "assets/brand/api-trailmap-logo.png", "schemas/inventory.schema.json", "examples/inventory.json"]
    missing = [name for name in required if not (ROOT / name).is_file()]
    if missing:
        raise SystemExit("Incomplete installation: " + ", ".join(missing))
    from generate import render, validate
    fixture = json.loads((ROOT / "examples/inventory.json").read_text(encoding="utf-8"))
    validate(fixture)
    with tempfile.TemporaryDirectory(prefix="api-trailmap-check-") as temp:
        generated = render(fixture, Path(temp) / "output")
        if not {"INDEX.md", "api-trailmap.html", "api-trailmap.json", "postman/api.postman_collection.json"}.issubset(generated):
            raise SystemExit("Generation smoke test failed")
    print("PASS: package files and isolated offline generation. No API calls made.")
    print("Host discovery is not verified by this script. Start a new session if needed and ask the agent to use API Trailmap.")


if __name__ == "__main__":
    main()
