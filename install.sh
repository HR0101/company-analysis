#!/usr/bin/env bash
set -euo pipefail

repository_url="https://github.com/HR0101/company-analysis-codex.git"
skill_name="company-analysis"

# 1. Install into ~/.agents/skills and ~/.codex/skills so both CLI and Desktop App discover the skill immediately
agents_skills_root="${CODEX_SKILLS_DIR:-${HOME}/.agents/skills}"
installation_codex_root="${CODEX_HOME:-${HOME}/.codex}"
codex_skills_root="${installation_codex_root}/skills"
marketplace_file="${HOME}/.agents/plugins/marketplace.json"

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is required to install ${skill_name}." >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is required to install ${skill_name}." >&2
  exit 1
fi

tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

echo "Fetching ${skill_name} from ${repository_url}..."
git clone --depth 1 "$repository_url" "${tmp_dir}/repo" >/dev/null 2>&1

# Validate the existing registration before replacing any installed files.
marketplace_updater="${tmp_dir}/repo/tools/update_marketplace.py"
python3 "$marketplace_updater" "$marketplace_file" "${installation_codex_root}/plugins/${skill_name}" --check >/dev/null

mkdir -p "$agents_skills_root" "$codex_skills_root" "${installation_codex_root}/plugins" "${HOME}/.agents/plugins"

rm -rf "${agents_skills_root}/${skill_name}" "${codex_skills_root}/${skill_name}" "${installation_codex_root}/plugins/${skill_name}"
cp -R "${tmp_dir}/repo/skills/${skill_name}" "${agents_skills_root}/${skill_name}"
cp -R "${tmp_dir}/repo/skills/${skill_name}" "${codex_skills_root}/${skill_name}"
cp -R "${tmp_dir}/repo/plugins/${skill_name}" "${installation_codex_root}/plugins/${skill_name}"

# 2. Register in ~/.agents/plugins/marketplace.json for the ChatGPT / Codex Desktop App if not already present
marketplace_name="$(python3 "$marketplace_updater" "$marketplace_file" "${installation_codex_root}/plugins/${skill_name}")"

# 3. If codex CLI (or ChatGPT.app bundled codex CLI) is available, register & enable the plugin for Desktop App
codex_bin=""
if command -v codex >/dev/null 2>&1; then
  codex_bin="$(command -v codex)"
elif [[ -x "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex" ]]; then
  codex_bin="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"
fi

if [[ -n "$codex_bin" ]]; then
  if ! "$codex_bin" plugin add "company-analysis@${marketplace_name}"; then
    echo "Warning: files were installed, but plugin activation failed. Retry: codex plugin add company-analysis@${marketplace_name}" >&2
  fi
fi

echo "Installation complete!"
echo "  - Skill installed to:  ${codex_skills_root}/${skill_name} and ${agents_skills_root}/${skill_name}"
echo "  - Plugin installed to: ${installation_codex_root}/plugins/${skill_name}"
echo "Invoke the skill with: \$${skill_name}"
echo "If the ChatGPT / Codex desktop app is open, restart it or open a new thread to load the plugin."
