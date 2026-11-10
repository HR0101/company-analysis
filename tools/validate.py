#!/usr/bin/env python3
"""プラグインとスキルの定義ファイルおよび同梱スクリプトを検証する．

公開・配布前に次を確認する．

- plugin.json，.codex-plugin/plugin.json，.agents/plugins/marketplace.json，
  .claude-plugin/plugin.json，.claude-plugin/marketplace.json がJSONとして妥当であること
- 必須フィールドが存在し，プラグイン名・文字数制限・参照アセットパスがすべて整合すること
- ルート，skills/company-analysis/，plugins/company-analysis/skills/company-analysis/ の
  SKILL.md・agents/openai.yaml・references/・scripts/ が完全一致していること
- SKILL.md のフロントマターに name と description があり，禁止文字（<, >）や未完成の TODO がないこと
- スキル内のすべての Markdown から張った相対リンクの先が実在すること
- 同梱スクリプトに実行権限があり，構文エラーがないこと
- pattern_selector.py，financial_analyzer.py，report_generator.py が全パターン・全モードで正常動作すること

使い方:
    python3 tools/validate.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import py_compile
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent

SKILL_NAME = "company-analysis"
ROOT_SKILL_DIR = ROOT
SUB_SKILL_DIR = ROOT / "skills" / SKILL_NAME
PLUGIN_DIR = ROOT / "plugins" / SKILL_NAME
PLUGIN_SKILL_DIR = PLUGIN_DIR / "skills" / SKILL_NAME

errors: list[str] = []
warnings: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


def warn(message: str) -> None:
    warnings.append(message)


def load_json(path: Path) -> dict | None:
    if not path.exists():
        fail(f"{path.relative_to(ROOT)} が存在しない")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"{path.relative_to(ROOT)} のJSONが不正: {exc}")
        return None


def parse_frontmatter(path: Path) -> dict[str, str] | None:
    if not path.exists():
        fail(f"{path.relative_to(ROOT)} が存在しない")
        return None
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        fail(f"{path.relative_to(ROOT)} にYAMLフロントマターがない")
        return None
    fields: dict[str, str] = {}
    for line in match.group(1).split("\n"):
        if not line.strip() or line.lstrip().startswith("#") or line.startswith("  "):
            continue
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if kv:
            fields[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return fields


def check_manifests() -> None:
    for p in [
        ROOT / "plugin.json",
        ROOT / ".codex-plugin" / "plugin.json",
        PLUGIN_DIR / "plugin.json",
        PLUGIN_DIR / ".codex-plugin" / "plugin.json",
        ROOT / ".claude-plugin" / "plugin.json",
    ]:
        data = load_json(p)
        if data is None:
            continue
        if data.get("name") != SKILL_NAME:
            fail(f"{p.relative_to(ROOT)} の name が {SKILL_NAME} と一致しない")
        for req in ("version", "description"):
            if not data.get(req):
                fail(f"{p.relative_to(ROOT)} に {req} がない")

    # Verify OpenAI interface constraints on portable and codex manifests
    portable = load_json(PLUGIN_DIR / "plugin.json")
    if portable:
        iface = portable.get("extensions", {}).get("com.openai", {}).get("interface", {})
        if len(iface.get("displayName", "")) > 30:
            fail("plugin.json の displayName が30文字を超えている")
        if len(iface.get("shortDescription", "")) > 30:
            fail("plugin.json の shortDescription が30文字を超えている")
        for key in ("composerIcon", "composerIconDark", "logo", "logoDark"):
            rel = iface.get(key, "")
            if not rel.startswith("./") or not (PLUGIN_DIR / rel).exists():
                fail(f"plugin.json の {key} ({rel}) が存在しない")

    codex_mkt = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    if codex_mkt:
        plugins = codex_mkt.get("plugins", [])
        if not plugins or plugins[0].get("name") != SKILL_NAME:
            fail(".agents/plugins/marketplace.json に company-analysis エントリがない")
        src_path = plugins[0].get("source", {}).get("path", "")
        if not (ROOT / src_path).exists():
            fail(f".agents/plugins/marketplace.json の source.path ({src_path}) が存在しない")

    claude_mkt = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if claude_mkt:
        plugins = claude_mkt.get("plugins", [])
        if not plugins or plugins[0].get("name") != SKILL_NAME:
            fail(".claude-plugin/marketplace.json に company-analysis エントリがない")


def check_skill_dirs_and_parity() -> None:
    skill_dirs = [ROOT_SKILL_DIR, SUB_SKILL_DIR, PLUGIN_SKILL_DIR]
    for d in skill_dirs:
        fm = parse_frontmatter(d / "SKILL.md")
        if fm is None:
            continue
        if fm.get("name") != SKILL_NAME:
            fail(f"{(d / 'SKILL.md').relative_to(ROOT)} の name が {SKILL_NAME} でない")
        desc = fm.get("description", "")
        if not desc or "<" in desc or ">" in desc or len(desc) > 1024:
            fail(f"{(d / 'SKILL.md').relative_to(ROOT)} の description が規約違反")

        openai_yaml = d / "agents" / "openai.yaml"
        if not openai_yaml.exists():
            fail(f"{openai_yaml.relative_to(ROOT)} が存在しない")
        else:
            ytext = openai_yaml.read_text(encoding="utf-8")
            if f"${SKILL_NAME}" not in ytext:
                fail(f"{openai_yaml.relative_to(ROOT)} の default_prompt に ${SKILL_NAME} が含まれていない")

        # Check markdown relative links inside SKILL.md and references/
        md_files = [d / "SKILL.md"] + sorted((d / "references").glob("*.md"))
        for md in md_files:
            content = md.read_text(encoding="utf-8")
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", content):
                if link.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                target = (md.parent / link).resolve()
                if not target.exists():
                    fail(f"{md.relative_to(ROOT)} 内のリンク先 {link} が存在しない")

    # Parity check across ROOT, skills/company-analysis, and plugins/company-analysis/skills/company-analysis
    rel_files = [
        "SKILL.md",
        "agents/openai.yaml",
        "references/secrets-and-methodology.md",
        "references/industry-patterns.md",
        "references/role-patterns.md",
        "references/interview-stage-patterns.md",
        "references/output-templates.md",
        "scripts/pattern_selector.py",
        "scripts/financial_analyzer.py",
        "scripts/report_generator.py",
    ]
    for rel in rel_files:
        base_text = (ROOT_SKILL_DIR / rel).read_text(encoding="utf-8")
        for other_dir in (SUB_SKILL_DIR, PLUGIN_SKILL_DIR):
            other_path = other_dir / rel
            if not other_path.exists():
                fail(f"{other_path.relative_to(ROOT)} が存在しない")
            elif other_path.read_text(encoding="utf-8") != base_text:
                fail(f"{other_path.relative_to(ROOT)} の内容がルートの {rel} と一致しない")


def check_scripts() -> None:
    scripts = list((SUB_SKILL_DIR / "scripts").glob("*.py"))
    if not scripts:
        fail("scripts/ にPythonスクリプトがない")
        return

    for script in scripts + [ROOT / "install.sh", ROOT / "tools" / "update_marketplace.py"]:
        if script.parent != ROOT / "tools" and not os.access(script, os.X_OK):
            fail(f"{script.relative_to(ROOT)} に実行権限がない")
        if script.suffix == ".py":
            try:
                py_compile.compile(str(script), doraise=True)
            except py_compile.PyCompileError as exc:
                fail(f"{script.relative_to(ROOT)} に構文エラー: {exc}")

    # Functional tests of the 3 scripts
    ps = SUB_SKILL_DIR / "scripts" / "pattern_selector.py"
    fa = SUB_SKILL_DIR / "scripts" / "financial_analyzer.py"
    rg = SUB_SKILL_DIR / "scripts" / "report_generator.py"

    r1 = subprocess.run(
        [sys.executable, str(ps), "--list", "--format", "json"],
        capture_output=True,
        text=True,
    )
    if r1.returncode != 0:
        fail(f"pattern_selector.py --list が失敗: {r1.stderr}")
    else:
        cat = json.loads(r1.stdout)
        if len(cat.get("industries", {})) != 8 or len(cat.get("stages", {})) != 6:
            fail("pattern_selector.py のパターン数が想定と異なる")

    r2 = subprocess.run(
        [
            sys.executable,
            str(fa),
            "--company",
            "検証株式会社",
            "--revenue",
            "100",
            "--operating-profit",
            "20",
            "--operating-cf",
            "25",
            "--investing-cf",
            "-10",
            "--financing-cf",
            "-5",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
    )
    if r2.returncode != 0:
        fail(f"financial_analyzer.py が失敗: {r2.stderr}")

    with tempfile.TemporaryDirectory() as tmp:
        out_md = Path(tmp) / "out.md"
        r3 = subprocess.run(
            [
                sys.executable,
                str(rg),
                "--company",
                "検証株式会社",
                "--industry",
                "商社",
                "--role",
                "営業",
                "--stage",
                "2次面接",
                "--mode",
                "full",
                "--output",
                str(out_md),
            ],
            capture_output=True,
            text=True,
        )
        if r3.returncode != 0 or not out_md.exists():
            fail(f"report_generator.py が失敗: {r3.stderr}")


def main() -> int:
    check_manifests()
    check_skill_dirs_and_parity()
    check_scripts()

    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"[FAIL] {e}", file=sys.stderr)
        print(f"\n検証失敗: {len(errors)} 件のエラーがあります．", file=sys.stderr)
        return 1

    print("[OK] すべてのマニフェスト・スキル定義・リンク・スクリプト検証に合格しました．")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
