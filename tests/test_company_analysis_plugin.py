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
import importlib.util
import itertools
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "company-analysis"
SKILL_DIR = PLUGIN_DIR / "skills" / "company-analysis"
SCRIPTS_DIR = SKILL_DIR / "scripts"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


financial = load_module("financial", SCRIPTS_DIR / "financial_analyzer.py")
patterns = load_module("patterns", SCRIPTS_DIR / "pattern_selector.py")
marketplace = load_module("marketplace", REPO_ROOT / "tools" / "update_marketplace.py")


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
        # Known financial ratios and four provided review scores.
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
                "--ow-evaluation",
                "3.7",
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
        self.assertTrue(d1["cash_flow_diagnosis"]["operating_cf_covers_investing_outflow"])
        self.assertEqual(d1["cash_flow_diagnosis"]["cash_change_before_fx"], 20.0)
        self.assertEqual(d1["human_capital_diagnosis"]["missing_scores"], [])
        self.assertEqual(d1["human_capital_diagnosis"]["provided_scores"]["evaluation"], 3.7)

        # Contrasting growth/compliance scores must not invent a low evaluation score.
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
                "--ow-evaluation",
                "5.0",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        d2 = json.loads(res2.stdout)
        hc = d2["human_capital_diagnosis"]
        self.assertEqual(hc["provided_scores"]["evaluation"], 5.0)
        evaluation_finding = next(f for f in hc["findings"] if f.startswith("口コミの人事評価"))
        self.assertIn("5.0/5", evaluation_finding)
        self.assertNotIn("低め", evaluation_finding)

    def test_missing_review_scores_are_not_inferred(self):
        for supplied in [{}, {"ow_overall": 4.0}, {"ow_evaluation": 5.0}]:
            with self.subTest(supplied=supplied):
                args = dict.fromkeys([
                    "avg_age", "avg_tenure", "avg_salary_man", "ow_overall",
                    "ow_growth20s", "ow_compliance", "ow_evaluation",
                ])
                args.update(supplied)
                result = financial.diagnose_human_capital(**args)
                self.assertEqual(len(result["provided_scores"]), len(supplied))
                self.assertEqual(len(result["missing_scores"]), 4 - len(supplied))
                self.assertNotIn("優良組織", " ".join(result["findings"]))
                self.assertNotIn("ホワイト", result["organization_archetype"])

    def test_review_scores_outside_scale_are_rejected(self):
        for value in [0, 6, float("nan"), float("inf")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                financial.diagnose_human_capital(None, None, None, value, None, None, None)

    def test_cf_signs_do_not_override_amounts(self):
        shortfall = financial.diagnose_cash_flow(1, -100, -100)
        covered = financial.diagnose_cash_flow(300, -100, -100)
        self.assertEqual(shortfall["sign_pattern"], covered["sign_pattern"])
        self.assertEqual(shortfall["free_cf"], -99)
        self.assertEqual(shortfall["cash_change_before_fx"], -199)
        self.assertFalse(shortfall["operating_cf_covers_investing_outflow"])
        self.assertTrue(covered["operating_cf_covers_investing_outflow"])
        self.assertNotIn("健全", shortfall["diagnosis"])

    def test_cf_all_sign_patterns_and_zero(self):
        patterns_seen = set()
        for values in itertools.product([-10, 10], repeat=3):
            result = financial.diagnose_cash_flow(*values)
            patterns_seen.add(tuple(result["sign_pattern"]))
            self.assertEqual(result["cash_change_before_fx"], sum(values))
        self.assertEqual(len(patterns_seen), 8)
        for values in [(0, 0, 0), (10, 0, -5), (10, -5, 0)]:
            result = financial.diagnose_cash_flow(*values)
            self.assertIn("zero", result["sign_pattern"])
        with self.assertRaises(ValueError):
            financial.diagnose_cash_flow(float("nan"), 1, 2)

    def test_pattern_annotations_and_invalid_inputs(self):
        for query, expected in [
            ("2次面接（現場部長クラス）", "second-interview"),
            ("２次面接（部長）", "second-interview"),
            ("1次面接（人事）", "first-interview"),
            ("最終面接（役員）", "final-interview"),
            ("2", "first-interview"),  # Exact menu number, not an interview round.
        ]:
            with self.subTest(query=query):
                self.assertEqual(patterns.resolve_pattern(query, patterns.STAGE_PATTERNS, "first-interview"), expected)
        self.assertEqual(patterns.resolve_pattern("第二新卒（社会人2年目）", patterns.CANDIDATE_PATTERNS, "new-grad"), "second-new-grad")
        with self.assertRaises(ValueError):
            patterns.resolve_pattern("4次面接", patterns.STAGE_PATTERNS, "first-interview")
        self.assertEqual(patterns.resolve_pattern("", patterns.ROLE_PATTERNS, "sales-cs"), "sales-cs")
        for script in ["pattern_selector.py", "report_generator.py"]:
            for query in ["存在しない職種", "エンジニア・コンサルタント"]:
                with self.subTest(script=script, query=query):
                    result = subprocess.run([sys.executable, str(SCRIPTS_DIR / script), "--role", query], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 2)
                    self.assertEqual(result.stdout, "")
                    self.assertNotIn("Traceback", result.stderr)

    def test_readme_local_cli_examples(self):
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        count = 0
        with tempfile.TemporaryDirectory() as tmp:
            for block in re.findall(r"```bash\n(.*?)```", readme, re.S):
                for line in block.replace("\\\n", " ").splitlines():
                    if not line.startswith("python3 scripts/"):
                        continue
                    command = shlex.split(line)
                    command[0] = sys.executable
                    if "--output" in command:
                        command[command.index("--output") + 1] = str(Path(tmp) / "report.md")
                    result = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    count += 1
        self.assertEqual(count, 4)

    def test_marketplace_invalid_data_is_preserved(self):
        for original in ['{"plugins": [', '[]', '{"name":"mine","plugins":{}}', '{"name":"mine","plugins":[null]}']:
            with self.subTest(original=original), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "marketplace.json"
                path.write_text(original, encoding="utf-8")
                for check in [True, False]:
                    with self.assertRaises(ValueError):
                        marketplace.update_marketplace(path, Path(tmp) / "plugin", check)
                    self.assertEqual(path.read_text(encoding="utf-8"), original)
                    self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_marketplace_preserves_other_plugins_and_backups(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "marketplace.json"
            original = '{"name":"mine","custom":true,"plugins":[{"name":"other","extra":1},{"name":"company-analysis"}]}'
            path.write_text(original, encoding="utf-8")
            plugin_dir = Path(tmp) / "custom-codex" / "plugins" / "company-analysis"
            self.assertEqual(marketplace.update_marketplace(path, plugin_dir, True), "mine")
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(tmp).glob("*.bak")), [])
            marketplace.update_marketplace(path, plugin_dir)
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(data["custom"])
            self.assertEqual(data["plugins"][0], {"name": "other", "extra": 1})
            self.assertEqual(data["plugins"][1]["source"]["path"], str(plugin_dir.resolve()))
            backups = list(Path(tmp).glob("*.bak"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), original)
            marketplace.update_marketplace(path, plugin_dir)
            self.assertEqual(len(list(Path(tmp).glob("*.bak"))), 2)
            self.assertEqual(len(json.loads(path.read_text())["plugins"]), 2)

    def test_marketplace_write_failure_preserves_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "marketplace.json"
            original = '{"name":"mine","plugins":[{"name":"other"}]}'
            path.write_text(original, encoding="utf-8")
            with mock.patch.object(marketplace.os, "replace", side_effect=OSError("simulated failure")):
                with self.assertRaises(OSError):
                    marketplace.update_marketplace(path, Path(tmp) / "plugin")
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])

    def test_marketplace_can_be_created_without_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "nested" / "marketplace.json"
            marketplace.update_marketplace(path, Path(tmp) / "plugin", True)
            self.assertFalse(path.parent.exists())
            marketplace.update_marketplace(path, Path(tmp) / "plugin")
            self.assertEqual(json.loads(path.read_text())["plugins"][0]["name"], "company-analysis")
            self.assertEqual(list(path.parent.glob("*.bak")), [])

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
