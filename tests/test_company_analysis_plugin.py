#!/usr/bin/env python3
"""
Comprehensive automated test suite for the `company-analysis` Codex Skill Plugin.
Tests:
1. Portable & Codex compatibility plugin manifests and marketplace JSONs
2. SKILL.md frontmatter, progressive disclosure reference links, and agents/openai.yaml
3. pattern_selector.py across all 5 axes & Japanese fuzzy aliases
4. financial_analyzer.py across all 8 CF patterns & OpenWork gap archetypes
5. report_generator.py across full, cheatsheet, and offer-comparison modes
6. Internal parity across root, skills/company-analysis, and plugins/company-analysis/skills/company-analysis
"""

import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "company-analysis"
SKILL_DIR = PLUGIN_DIR / "skills" / "company-analysis"
SCRIPTS_DIR = SKILL_DIR / "scripts"


class TestCompanyAnalysisPlugin(unittest.TestCase):
    def test_plugin_manifests_and_assets(self):
        portable_manifest_path = PLUGIN_DIR / "plugin.json"
        codex_manifest_path = PLUGIN_DIR / ".codex-plugin" / "plugin.json"
        marketplace_path = REPO_ROOT / ".agents" / "plugins" / "marketplace.json"

        self.assertTrue(portable_manifest_path.exists(), "Missing plugin.json")
        self.assertTrue(codex_manifest_path.exists(), "Missing .codex-plugin/plugin.json")
        self.assertTrue(marketplace_path.exists(), "Missing .agents/plugins/marketplace.json")

        portable = json.loads(portable_manifest_path.read_text(encoding="utf-8"))
        codex_m = json.loads(codex_manifest_path.read_text(encoding="utf-8"))
        mkt = json.loads(marketplace_path.read_text(encoding="utf-8"))

        self.assertEqual(portable["name"], "company-analysis")
        self.assertEqual(codex_m["name"], "company-analysis")

        oai_ext = portable["extensions"]["com.openai"]
        iface = oai_ext["interface"]
        self.assertLessEqual(len(iface["displayName"]), 30)
        self.assertLessEqual(len(iface["shortDescription"]), 30)
        self.assertLessEqual(len(iface["defaultPrompt"]), 3)
        for p in iface["defaultPrompt"]:
            self.assertLessEqual(len(p), 128)

        # Verify referenced files exist relative to PLUGIN_DIR
        for rel_key in ["composerIcon", "composerIconDark", "logo", "logoDark"]:
            rel_path = iface[rel_key]
            self.assertTrue(rel_path.startswith("./"))
            target = (PLUGIN_DIR / rel_path).resolve()
            self.assertTrue(target.exists(), f"Missing asset {target}")

        onboarding = (PLUGIN_DIR / oai_ext["onboardingSkill"]).resolve()
        self.assertTrue(onboarding.exists(), "Missing onboardingSkill SKILL.md")

        # Verify marketplace entry resolves to PLUGIN_DIR
        self.assertEqual(len(mkt["plugins"]), 1)
        entry = mkt["plugins"][0]
        self.assertEqual(entry["name"], "company-analysis")
        resolved_plugin_dir = (REPO_ROOT / entry["source"]["path"]).resolve()
        self.assertEqual(resolved_plugin_dir, PLUGIN_DIR.resolve())

    def test_skill_structure_and_links(self):
        skill_md = SKILL_DIR / "SKILL.md"
        openai_yaml = SKILL_DIR / "agents" / "openai.yaml"
        self.assertTrue(skill_md.exists())
        self.assertTrue(openai_yaml.exists())

        text = skill_md.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        # Ensure all markdown links in SKILL.md exist
        links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        self.assertGreaterEqual(len(links), 5)
        for link in links:
            target = (SKILL_DIR / link).resolve()
            self.assertTrue(target.exists(), f"Broken link in SKILL.md: {link}")

        yaml_text = openai_yaml.read_text(encoding="utf-8")
        self.assertIn("$company-analysis", yaml_text)

    def test_pattern_selector_all_axes_and_aliases(self):
        script = SCRIPTS_DIR / "pattern_selector.py"
        res_list = subprocess.run(
            [sys.executable, str(script), "--list", "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        catalog = json.loads(res_list.stdout)
        self.assertEqual(len(catalog["industries"]), 8)
        self.assertEqual(len(catalog["roles"]), 6)
        self.assertEqual(len(catalog["stages"]), 6)
        self.assertEqual(len(catalog["candidates"]), 3)
        self.assertEqual(len(catalog["archetypes"]), 4)

        # Test Japanese fuzzy alias resolution
        res_bp = subprocess.run(
            [
                sys.executable,
                str(script),
                "--company",
                "三菱商事",
                "--industry",
                "総合商社",
                "--role",
                "事業企画",
                "--stage",
                "最終面接",
                "--candidate",
                "新卒",
                "--archetype",
                "日系大手",
                "--competitors",
                "三井物産,伊藤忠商事",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        bp = json.loads(res_bp.stdout)
        self.assertEqual(bp["selected_patterns"]["industry"]["id"], "trading")
        self.assertEqual(bp["selected_patterns"]["role"]["id"], "planning-marketing-bizdev")
        self.assertEqual(bp["selected_patterns"]["stage"]["id"], "final-interview")
        self.assertEqual(bp["selected_patterns"]["candidate"]["id"], "new-grad")
        self.assertEqual(bp["selected_patterns"]["archetype"]["id"], "listed-enterprise")
        self.assertEqual(bp["competitors"], ["三井物産", "伊藤忠商事"])

    def test_financial_analyzer_cf_and_human_capital(self):
        script = SCRIPTS_DIR / "financial_analyzer.py"
        # Case 1: Healthy growth + White company
        res1 = subprocess.run(
            [
                sys.executable,
                str(script),
                "--company",
                "優良テック社",
                "--revenue",
                "200",
                "--prev-revenue",
                "150",
                "--gross-profit",
                "160",
                "--operating-profit",
                "40",
                "--net-profit",
                "28",
                "--total-assets",
                "300",
                "--equity",
                "180",
                "--employees",
                "400",
                "--operating-cf",
                "50",
                "--investing-cf",
                "-20",
                "--financing-cf",
                "-10",
                "--avg-age",
                "33.0",
                "--avg-tenure",
                "5.5",
                "--avg-salary",
                "850",
                "--ow-overall",
                "4.1",
                "--ow-growth20s",
                "4.2",
                "--ow-compliance",
                "3.9",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        d1 = json.loads(res1.stdout)
        self.assertEqual(d1["metrics"]["operating_margin_pct"], 20.0)
        self.assertGreater(d1["metrics"]["rule_of_40_score"], 50.0)
        self.assertIn("王道・優良成長型", d1["cash_flow_diagnosis"]["pattern_label"])
        self.assertIn("真のホワイト", d1["human_capital_diagnosis"]["organization_archetype"])

        # Case 2: Yuru-black detection
        res2 = subprocess.run(
            [
                sys.executable,
                str(script),
                "--company",
                "まったり社",
                "--ow-overall",
                "3.2",
                "--ow-growth20s",
                "2.3",
                "--ow-compliance",
                "4.2",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        d2 = json.loads(res2.stdout)
        self.assertIn("ゆるブラック", d2["human_capital_diagnosis"]["organization_archetype"])

    def test_report_generator_modes(self):
        script = SCRIPTS_DIR / "report_generator.py"
        for mode, expected_header in [
            ("full", "【企業分析＆選考突破マスターシート】"),
            ("cheatsheet", "【面接直前5分チートシート】"),
            ("offer-comparison", "【内定比較・オファー面談意思決定シート】"),
        ]:
            with tempfile.TemporaryDirectory() as tmpdir:
                out_file = Path(tmpdir) / f"report_{mode}.md"
                subprocess.run(
                    [
                        sys.executable,
                        str(script),
                        "--company",
                        "テスト株式会社",
                        "--industry",
                        "IT",
                        "--role",
                        "エンジニア",
                        "--stage",
                        "2次面接",
                        "--mode",
                        mode,
                        "--output",
                        str(out_file),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertTrue(out_file.exists())
                content = out_file.read_text(encoding="utf-8")
                self.assertIn(expected_header, content)
                self.assertIn("テスト株式会社", content)

    def test_internal_parity_across_skill_locations(self):
        root_skill = REPO_ROOT / "SKILL.md"
        sub_skill = REPO_ROOT / "skills" / "company-analysis" / "SKILL.md"
        plugin_skill = SKILL_DIR / "SKILL.md"
        self.assertEqual(
            root_skill.read_text(encoding="utf-8"),
            sub_skill.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            root_skill.read_text(encoding="utf-8"),
            plugin_skill.read_text(encoding="utf-8"),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
