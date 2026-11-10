#!/usr/bin/env bash
set -euo pipefail

repository_url="https://github.com/HR0101/company-analysis-codex.git"
skill_name="company-analysis"

# 1. Install into ~/.agents/skills and ~/.codex/skills so both CLI and Desktop App discover the skill immediately
agents_skills_root="${CODEX_SKILLS_DIR:-${HOME}/.agents/skills}"
codex_home="${CODEX_HOME:-${HOME}/.codex}"
codex_skills_root="${codex_home}/skills"

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required to install ${skill_name}." >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

echo "Fetching ${skill_name} from ${repository_url}..."
git clone --depth 1 "$repository_url" "${tmp_dir}/repo" >/dev/null 2>&1

mkdir -p "$agents_skills_root" "$codex_skills_root" "${codex_home}/plugins" "${HOME}/.agents/plugins"

rm -rf "${agents_skills_root}/${skill_name}" "${codex_skills_root}/${skill_name}" "${codex_home}/plugins/${skill_name}"
cp -R "${tmp_dir}/repo/skills/${skill_name}" "${agents_skills_root}/${skill_name}"
cp -R "${tmp_dir}/repo/skills/${skill_name}" "${codex_skills_root}/${skill_name}"
cp -R "${tmp_dir}/repo/plugins/${skill_name}" "${codex_home}/plugins/${skill_name}"

# 2. Register in ~/.agents/plugins/marketplace.json for the ChatGPT / Codex Desktop App if not already present
marketplace_file="${HOME}/.agents/plugins/marketplace.json"
python3 - "$marketplace_file" << 'PY'
import json
from pathlib import Path
import sys

mkt_path = Path(sys.argv[1])
entry = {
    "name": "company-analysis",
    "source": {
        "source": "local",
        "path": "./.codex/plugins/company-analysis"
    },
    "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
    },
    "category": "Productivity"
}

if mkt_path.exists():
    try:
        data = json.loads(mkt_path.read_text(encoding="utf-8"))
    except Exception:
        data = {"name": "personal-plugins", "interface": {"displayName": "Personal Codex Plugins"}, "plugins": []}
else:
    data = {"name": "personal-plugins", "interface": {"displayName": "Personal Codex Plugins"}, "plugins": []}

plugins = data.setdefault("plugins", [])
plugins = [p for p in plugins if p.get("name") != "company-analysis"]
plugins.append(entry)
data["plugins"] = plugins
mkt_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

# 3. If codex CLI (or ChatGPT.app bundled codex CLI) is available, register & enable the plugin for Desktop App
codex_bin=""
if command -v codex >/dev/null 2>&1; then
  codex_bin="$(command -v codex)"
elif [[ -x "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex" ]]; then
  codex_bin="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"
fi

if [[ -n "$codex_bin" ]]; then
  "$codex_bin" plugin add company-analysis@personal-plugins >/dev/null 2>&1 || true
fi

echo "Installation complete!"
echo "  - Skill installed to:  ${codex_skills_root}/${skill_name} and ${agents_skills_root}/${skill_name}"
echo "  - Plugin installed to: ${codex_home}/plugins/${skill_name}"
echo "Invoke the skill with: \$${skill_name}"
echo "If the ChatGPT / Codex desktop app is open, restart it or open a new thread to load the plugin."
