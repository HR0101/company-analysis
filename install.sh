#!/usr/bin/env bash
set -euo pipefail

repository_url="https://github.com/HR0101/company-analysis.git"
repo_slug="HR0101/company-analysis"
skill_name="company-analysis"

# Target selection: default installs for both Codex and Claude (--codex or --claude to limit)
target_mode="both"
if [[ "${1:-}" == "--codex" ]]; then
  target_mode="codex"
elif [[ "${1:-}" == "--claude" ]]; then
  target_mode="claude"
fi

agents_skills_root="${CODEX_SKILLS_DIR:-${HOME}/.agents/skills}"
installation_codex_root="${CODEX_HOME:-${HOME}/.codex}"
codex_skills_root="${installation_codex_root}/skills"
marketplace_file="${HOME}/.agents/plugins/marketplace.json"

claude_home="${CLAUDE_CONFIG_DIR:-${HOME}/.claude}"
claude_skills_root="${claude_home}/skills"

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

if [[ "$target_mode" == "both" || "$target_mode" == "codex" ]]; then
  # Validate the existing Codex marketplace registration before replacing any installed files.
  marketplace_updater="${tmp_dir}/repo/tools/update_marketplace.py"
  python3 "$marketplace_updater" "$marketplace_file" "${installation_codex_root}/plugins/${skill_name}" --check >/dev/null

  mkdir -p "$agents_skills_root" "$codex_skills_root" "${installation_codex_root}/plugins" "${HOME}/.agents/plugins"

  rm -rf "${agents_skills_root}/${skill_name}" "${codex_skills_root}/${skill_name}" "${installation_codex_root}/plugins/${skill_name}"
  cp -R "${tmp_dir}/repo/skills/${skill_name}" "${agents_skills_root}/${skill_name}"
  cp -R "${tmp_dir}/repo/skills/${skill_name}" "${codex_skills_root}/${skill_name}"
  cp -R "${tmp_dir}/repo/plugins/${skill_name}" "${installation_codex_root}/plugins/${skill_name}"

  marketplace_name="$(python3 "$marketplace_updater" "$marketplace_file" "${installation_codex_root}/plugins/${skill_name}")"

  codex_bin=""
  if command -v codex >/dev/null 2>&1; then
    codex_bin="$(command -v codex)"
  elif [[ -x "/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex" ]]; then
    codex_bin="/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex"
  fi

  if [[ -n "$codex_bin" ]]; then
    if ! "$codex_bin" plugin add "company-analysis@${marketplace_name}"; then
      echo "Warning: Codex files were installed, but plugin activation failed. Retry: codex plugin add company-analysis@${marketplace_name}" >&2
    fi
  fi
fi

if [[ "$target_mode" == "both" || "$target_mode" == "claude" ]]; then
  claude_installed_as_plugin="false"
  if command -v claude >/dev/null 2>&1; then
    if claude plugin marketplace add "$repo_slug" >/dev/null 2>&1 || claude plugin marketplace update "$skill_name" >/dev/null 2>&1; then
      if claude plugin install "${skill_name}@${skill_name}" >/dev/null 2>&1; then
        claude_installed_as_plugin="true"
        rm -rf "${claude_skills_root}/${skill_name}"
      fi
    fi
  fi
  if [[ "$claude_installed_as_plugin" == "false" ]]; then
    mkdir -p "$claude_skills_root"
    rm -rf "${claude_skills_root}/${skill_name}"
    cp -R "${tmp_dir}/repo/skills/${skill_name}" "${claude_skills_root}/${skill_name}"
  fi
fi

echo "Installation complete!"
if [[ "$target_mode" == "both" || "$target_mode" == "codex" ]]; then
  echo "  - [Codex]  Skill installed to:  ${codex_skills_root}/${skill_name} and ${agents_skills_root}/${skill_name}"
  echo "  - [Codex]  Plugin installed to: ${installation_codex_root}/plugins/${skill_name} (Invoke with: \$${skill_name})"
fi
if [[ "$target_mode" == "both" || "$target_mode" == "claude" ]]; then
  echo "  - [Claude] Installed for Claude Code / Claude Desktop (Invoke with: /${skill_name}:${skill_name} or /${skill_name})"
fi
echo "If the ChatGPT / Codex desktop app or Claude Code is open, restart it or open a new session to load the plugin."
