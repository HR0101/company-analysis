#!/usr/bin/env python3
"""Validate, back up, and atomically update a local plugin marketplace."""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


def load_marketplace(path: Path) -> dict:
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {"name": "personal-plugins", "interface": {"displayName": "Personal Codex Plugins"}, "plugins": []}
    if not isinstance(data, dict) or not isinstance(data.get("name"), str) or not data["name"]:
        raise ValueError("marketplace must be an object with a non-empty name")
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list) or any(
        not isinstance(p, dict) or not isinstance(p.get("name"), str) for p in plugins
    ):
        raise ValueError("marketplace.plugins must be a list of named plugin objects")
    return data


def update_marketplace(path: Path, plugin_dir: Path, check_only: bool = False) -> str:
    # Read and validate before creating directories, backups, or replacement files.
    data = load_marketplace(path)
    if check_only:
        return data["name"]
    entry = {
        "name": "company-analysis",
        "source": {"source": "local", "path": str(plugin_dir.resolve())},
        "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        "category": "Productivity",
    }
    data["plugins"] = [p for p in data.get("plugins", []) if p["name"] != entry["name"]] + [entry]
    contents = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(contents)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            backup_fd, backup = tempfile.mkstemp(prefix=path.name + ".", suffix=".bak", dir=path.parent)
            os.close(backup_fd)
            shutil.copy2(path, backup)
            shutil.copymode(path, temporary)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return data["name"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("marketplace", type=Path)
    parser.add_argument("plugin_dir", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate without writing")
    args = parser.parse_args()
    try:
        print(update_marketplace(args.marketplace, args.plugin_dir, args.check))
    except (OSError, ValueError) as exc:
        print(f"Error: marketplace was not updated: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
