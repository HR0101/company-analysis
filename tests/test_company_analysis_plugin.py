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
input_ui = load_module("input_ui", SCRIPTS_DIR / "input_ui.py")
reports = load_module("reports", SCRIPTS_DIR / "report_generator.py")


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
        self.assertEqual(count, 5)

    def test_intake_initial_questions_accept_free_text(self):
        result = input_ui.prepare_intake({})
        self.assertEqual(result["tool"], "request_user_input_async")
        self.assertEqual([b["field"] for b in result["bindings"]], ["company", "purpose"])
        self.assertNotIn("options", result["arguments"]["questions"][0])
        self.assertEqual(len(result["arguments"]["questions"][1]["options"]), 3)

    def test_intake_research_does_not_ask_recruitment_questions(self):
        result = input_ui.prepare_intake({"company": "対象企業", "purpose": "research"})
        self.assertEqual([b["field"] for b in result["bindings"]], ["industry", "archetype"])
        ready = input_ui.prepare_intake({**result["state"], "industry": "auto", "archetype": "auto"})
        self.assertEqual(ready["status"], "ready")
        self.assertEqual(ready["configuration"]["output_mode"], "research")
        self.assertEqual(ready["unresolved_axes"], ["industry", "archetype"])
        self.assertEqual(input_ui.normalize_state({"industry": "おまかせ"})["industry"], "auto")

    def test_intake_only_requests_missing_fields(self):
        state = {"company": "対象企業", "purpose": "selection", "industry": "IT",
                 "role": "エンジニア", "stage": "2次面接", "candidate": "中途"}
        result = input_ui.prepare_intake(state)
        self.assertEqual([b["field"] for b in result["bindings"]], ["archetype", "output_mode"])
        self.assertEqual(result["state"]["role"], "software-ai-engineer")
        self.assertEqual(result["state"]["stage"], "second-interview")

    def test_intake_standard_choice_tree_covers_every_option(self):
        # Walk every branch to ensure a restricted UI can reach all canonical IDs,
        # including singleton leaves, without ever emitting a one-option question.
        for field, catalog in input_ui.CATALOGS.items():
            reached = set()
            state = {"company": "対象企業", "purpose": "selection", "industry": "auto",
                     "role": "auto", "stage": "auto", "candidate": "auto",
                     "archetype": "auto", "output_mode": "full", "reverse_question_count": 5}
            state.pop(field)
            queue = [state]
            while queue:
                branch = queue.pop()
                result = input_ui.prepare_intake(branch, "standard")
                if result["status"] == "ready":
                    reached.add(result["configuration"][field])
                    continue
                # Selecting offer-comparison reroutes to the offer workflow.
                if result["state"].get("purpose") == "offer":
                    reached.add(result["state"][field])
                    continue
                questions = result["arguments"]["questions"]
                self.assertLessEqual(len(questions), 3)
                self.assertEqual(len(questions), 1)
                self.assertGreaterEqual(len(questions[0]["options"]), 2)
                self.assertLessEqual(len(questions[0]["options"]), 3)
                for update in result["bindings"][0]["updates"].values():
                    queue.append({**result["state"], **update})
            self.assertEqual(reached, set(catalog) | {"auto"}, field)

    def test_intake_offer_routes_to_comparison(self):
        state = {"company": "第一志望社", "purpose": "offer", "industry": "auto",
                 "role": "software-ai-engineer", "candidate": "mid-career", "archetype": "auto"}
        result = input_ui.prepare_intake(state)
        self.assertEqual([b["field"] for b in result["bindings"]], ["competitors"])
        ready = input_ui.prepare_intake({**state, "competitors": "比較A社,比較B社"})
        self.assertEqual(ready["configuration"]["stage"], "offer-comparison")
        self.assertEqual(ready["configuration"]["output_mode"], "offer-comparison")

    def test_intake_text_fallback_and_state_validation(self):
        for ui in ("standard", "text"):
            result = input_ui.prepare_intake({}, ui)
            self.assertEqual(len(result["text_questions"]), 1 if ui == "standard" else 2)
        result = input_ui.prepare_intake({"company": "対象企業", "purpose": "research"}, "text")
        self.assertIsNone(result["tool"])
        self.assertIsNone(result["arguments"])
        self.assertEqual(len(result["text_questions"]), 2)
        for state in [[], {"purpose": "invalid"}, {"industry": "存在しない業界"},
                      {"candidate": 123}, {"industry_choices": ["unknown"]}]:
            with self.subTest(state=state), self.assertRaises(ValueError):
                input_ui.prepare_intake(state)

    def test_intake_cancellation_does_not_fill_unanswered_values(self):
        state = {"company": "対象企業", "purpose": "selection", "role": ""}
        first = input_ui.prepare_intake(state)
        second = input_ui.prepare_intake(first["state"])
        self.assertEqual(first, second)
        self.assertNotIn("role", second["state"])
        self.assertEqual(second["status"], "collecting")

    def test_intake_question_count_is_selected_after_output_mode(self):
        state = {"company": "対象企業", "purpose": "selection", "industry": "auto",
                 "role": "software-ai-engineer", "stage": "second-interview",
                 "candidate": "mid-career", "archetype": "auto"}
        result = input_ui.prepare_intake(state)
        self.assertEqual([b["field"] for b in result["bindings"]], ["output_mode"])
        result = input_ui.prepare_intake({**state, "output_mode": "full"})
        self.assertEqual([b["field"] for b in result["bindings"]], ["reverse_question_count"])
        self.assertEqual(result["bindings"][0]["updates"]["10問"], {"reverse_question_count": 10})
        for mode, default in [("full", 100), ("cheatsheet", 100)]:
            for value, expected in [("標準", default), ("7問", 7), (10, 10), ("不要（0問）", 0)]:
                with self.subTest(mode=mode, value=value):
                    ready = input_ui.prepare_intake({**state, "output_mode": mode, "reverse_question_count": value})
                    self.assertEqual(ready["configuration"]["reverse_question_count"], expected)

    def test_intake_standard_question_count_options_and_custom_input(self):
        base = {"company": "対象企業", "purpose": "selection", "industry": "auto",
                "role": "auto", "stage": "first-interview", "candidate": "new-grad",
                "archetype": "auto", "output_mode": "full"}
        queue, reached = [base], set()
        while queue:
            result = input_ui.prepare_intake(queue.pop(), "standard")
            if result["status"] == "ready":
                reached.add(result["configuration"]["reverse_question_count"])
                continue
            question = result["arguments"]["questions"][0]
            self.assertGreaterEqual(len(question["options"]), 2)
            self.assertLessEqual(len(question["options"]), 3)
            for updates in result["bindings"][0]["updates"].values():
                queue.append({**result["state"], **updates})
        self.assertEqual(reached, {0, 3, 5, 10, 100})
        for invalid in [-1, True, 2.5, "たくさん", "5.5", "-3問"]:
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                input_ui.prepare_intake({**base, "reverse_question_count": invalid})
        research = input_ui.prepare_intake({"company": "対象企業", "purpose": "research",
                                           "industry": "auto", "archetype": "auto", "reverse_question_count": 10})
        self.assertNotIn("reverse_question_count", research["configuration"])

    def test_report_question_count_matches_ui_configuration(self):
        base = {"company": "対象企業", "purpose": "selection", "industry": "it-saas-web",
                "role": "software-ai-engineer", "stage": "second-interview",
                "candidate": "mid-career", "archetype": "listed-enterprise"}
        for mode in ["full", "cheatsheet"]:
            for count in ["auto", 0, 1, 3, 5, 7, 10, 12, 100]:
                with self.subTest(mode=mode, count=count):
                    ready = input_ui.prepare_intake({**base, "output_mode": mode, "reverse_question_count": count})
                    expected = ready["configuration"]["reverse_question_count"]
                    command = [sys.executable, str(SCRIPTS_DIR / "report_generator.py"), "--mode", mode]
                    if count != "auto":
                        command.extend(["--reverse-question-count", str(expected)])
                    result = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    heading = re.search(r"^#{2,3} .*逆質問.*$", result.stdout, re.M)
                    if expected == 0:
                        self.assertIsNone(heading)
                        continue
                    self.assertIsNotNone(heading)
                    section = result.stdout[heading.end():]
                    numbers = re.findall(r"^(\d+)\. ", section, re.M)
                    self.assertEqual(numbers, [str(i) for i in range(1, expected + 1)])
        for invalid in ["-1", "2.5"]:
            result = subprocess.run([sys.executable, str(SCRIPTS_DIR / "report_generator.py"),
                                     "--reverse-question-count", invalid], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)

    def test_default_question_bank_has_100_distinct_questions_per_role(self):
        for role in patterns.ROLE_PATTERNS:
            bp = patterns.build_blueprint("対象企業", "it-saas-web", role, "first-interview",
                                          "new-grad", "listed-enterprise", [])
            output = reports.reverse_question_list(bp, 100)
            questions = re.findall(r"^\d+\. 「(.*)」$", output, re.M)
            self.assertEqual(len(questions), 100)
            self.assertEqual(len(set(questions)), 100)
            self.assertNotIn("を記入", output)
            for theme in reports.QUESTION_THEMES:
                self.assertEqual(sum(q.startswith(f"【{theme}】") for q in questions), 10)

    def test_self_introduction_is_separate_from_motivation(self):
        bp = patterns.build_blueprint("対象企業", "it-saas-web", "software-ai-engineer",
                                      "first-interview", "new-grad", "listed-enterprise", [])
        draft = "本日はお時間をいただきありがとうございます。大学で画像処理を研究しています。研究で検証を重ねた経験を生かし、開発に貢献したいと考えています。よろしくお願いいたします。"
        for generate in (reports.generate_full_report, reports.generate_cheatsheet):
            output = generate(bp, 0, draft)
            self.assertEqual(output.count(draft), 1)
            intro_heading = re.search(r"^#{2,3} .*自己紹介（約1分）", output, re.M)
            motivation_heading = re.search(r"^#{2,3} .*志望動機", output, re.M)
            self.assertLess(intro_heading.start(), motivation_heading.start())
            self.assertIn("自己紹介（約1分）", generate(bp, 0))
        with self.assertRaises(ValueError):
            reports.self_introduction_section("")

    def test_self_introduction_file_is_included_and_invalid_files_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = str(SCRIPTS_DIR / "report_generator.py")
            path = Path(tmp) / "intro.txt"
            draft = "本日はありがとうございます。大学で研究に取り組んでいます。よろしくお願いいたします。"
            path.write_text(draft, encoding="utf-8")
            for mode in ("full", "cheatsheet"):
                result = subprocess.run([sys.executable, script, "--mode", mode,
                                         "--self-introduction-file", str(path),
                                         "--reverse-question-count", "0"], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.count(draft), 1)
            path.write_text("  \n", encoding="utf-8")
            for invalid in (path, Path(tmp) / "missing.txt"):
                result = subprocess.run([sys.executable, script, "--self-introduction-file", str(invalid)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
            offer = subprocess.run([sys.executable, script, "--mode", "offer-comparison"],
                                    capture_output=True, text=True)
            self.assertNotIn("自己紹介", offer.stdout)

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
