#!/usr/bin/env python3
"""Prepare native question-tool arguments for the company-analysis intake.

This script does not display a window. The skill calls the available host tool
with the returned arguments, then merges the user's answers into the state.
"""

import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pattern_selector import (
    ARCHETYPE_PATTERNS, CANDIDATE_PATTERNS, INDUSTRY_PATTERNS,
    ROLE_PATTERNS, STAGE_PATTERNS, resolve_pattern,
)
from report_generator import DEFAULT_QUESTION_COUNTS, parse_question_count, resolve_question_count


CATALOGS = {
    "industry": INDUSTRY_PATTERNS,
    "role": ROLE_PATTERNS,
    "stage": STAGE_PATTERNS,
    "candidate": CANDIDATE_PATTERNS,
    "archetype": ARCHETYPE_PATTERNS,
}
LABELS = {
    "company": "対象企業・業界", "purpose": "分析目的", "industry": "業界",
    "role": "希望職種", "stage": "選考フェーズ", "candidate": "応募区分",
    "archetype": "企業タイプ", "output_mode": "出力形式", "competitors": "比較企業",
    "reverse_question_count": "逆質問の件数",
}
PURPOSES = {
    "research": "企業研究・IR・競合比較",
    "selection": "応募・面接対策",
    "offer": "内定・オファー比較",
}
OUTPUT_MODES = {"full": "フルレポート", "cheatsheet": "面接直前チートシート"}
SHORT_NAMES = {
    "it-saas-web": "IT・SaaS・Web", "consulting": "コンサル",
    "manufacturing": "メーカー", "trading": "商社", "finance": "金融",
    "media-ad-entertainment": "広告・メディア・エンタメ",
    "real-estate-infra-logistics": "不動産・インフラ・物流",
    "hr-retail-service-healthcare": "人材・小売・医療・サービス",
    "sales-cs": "営業・CS", "planning-marketing-bizdev": "企画・マーケ・事業開発",
    "pdm-pm-consultant": "PdM・PM・コンサル",
    "software-ai-engineer": "ソフトウェア・AI・データ",
    "rd-manufacturing-eng": "研究開発・設計・生産技術", "corporate": "管理部門",
    "casual-intern-ob": "カジュアル面談・OB訪問", "es-resume": "ES・書類選考",
    "first-interview": "1次面接", "second-interview": "2次・中盤面接",
    "final-interview": "最終・役員面接", "offer-comparison": "内定比較",
    "new-grad": "新卒", "mid-career": "中途", "second-new-grad": "第二新卒",
    "listed-enterprise": "日系大手・上場", "mega-venture": "メガベンチャー",
    "startup-unlisted": "未上場スタートアップ", "foreign-affiliated": "外資系",
}
AUTO_LABEL = "おまかせ・未定"
CHOICE_FIELDS = set(CATALOGS) | {"reverse_question_count"}


def options_for(field):
    if field == "reverse_question_count":
        return [("auto", "標準"), (3, "3問"), (5, "5問"), (10, "10問"), (100, "100問"), (0, "不要（0問）")]
    if field == "purpose":
        return list(PURPOSES.items())
    if field == "output_mode":
        return list(OUTPUT_MODES.items())
    options = [(key, SHORT_NAMES[key]) for key in CATALOGS[field]]
    return [("auto", AUTO_LABEL)] + options


def normalize_state(state):
    if not isinstance(state, dict):
        raise ValueError("stateはJSONオブジェクトで指定してください")
    allowed = set(LABELS) | {field + "_choices" for field in CHOICE_FIELDS}
    if set(state) - allowed:
        raise ValueError("未知の入力項目: " + ", ".join(sorted(set(state) - allowed)))
    normalized = {}
    for field, value in state.items():
        if field.endswith("_choices"):
            base = field.removesuffix("_choices")
            valid = {key for key, _ in options_for(base)}
            if not isinstance(value, list) or not value or any(v not in valid for v in value):
                raise ValueError(f"{field}の選択肢が不正です")
            normalized[field] = list(dict.fromkeys(value))
            continue
        if field == "reverse_question_count":
            if value == "":
                continue
            normalized[field] = parse_question_count(value)
            continue
        if not isinstance(value, str):
            raise ValueError(f"{field}は文字列で指定してください")
        value = value.strip()
        if not value:
            continue
        if field in CATALOGS:
            if value in ("auto", AUTO_LABEL, "おまかせ", "未定", "自動推定"):
                value = "auto"
            else:
                direct = {label: key for key, label in options_for(field)}
                value = direct[value] if value in direct else resolve_pattern(value, CATALOGS[field], "")
        elif field in ("purpose", "output_mode"):
            catalog = PURPOSES if field == "purpose" else {**OUTPUT_MODES, "research": "企業研究", "offer-comparison": "内定比較"}
            reverse = {label: key for key, label in catalog.items()}
            value = reverse.get(value, value)
            if value not in catalog:
                raise ValueError(f"{field}の指定が不正です: {value}")
        normalized[field] = value
    purpose = normalized.get("purpose")
    if purpose == "research":
        normalized["output_mode"] = "research"
    elif purpose == "offer":
        normalized.update(stage="offer-comparison", output_mode="offer-comparison")
    elif purpose == "selection":
        if normalized.get("output_mode") in ("research", "offer-comparison"):
            raise ValueError("選考対策の出力形式はfullまたはcheatsheetを選んでください")
        if normalized.get("stage") == "offer-comparison":
            normalized.update(purpose="offer", output_mode="offer-comparison")
    return normalized


def pending_fields(state):
    initial = [field for field in ("company", "purpose") if field not in state]
    if initial:
        return initial
    fields = ["industry", "archetype"]
    if state["purpose"] in ("selection", "offer"):
        fields = ["industry", "role", "stage", "candidate", "archetype", "output_mode"]
    if state["purpose"] == "offer":
        fields.insert(0, "competitors")
    if state["purpose"] == "selection" and "output_mode" in state:
        fields.append("reverse_question_count")
    return [field for field in fields if field not in state]


def prepare_intake(state, ui="async"):
    if ui not in ("async", "standard", "text"):
        raise ValueError("uiはasync、standard、textのいずれかを指定してください")
    state = normalize_state(state)
    pending = pending_fields(state)
    if not pending:
        configuration = {k: v for k, v in state.items() if not k.endswith("_choices")}
        if configuration["purpose"] == "selection":
            configuration["reverse_question_count"] = resolve_question_count(
                configuration["reverse_question_count"], configuration["output_mode"])
        else:
            configuration.pop("reverse_question_count", None)
        return {"status": "ready", "configuration": configuration,
                "unresolved_axes": [k for k in CATALOGS if configuration.get(k) == "auto"]}

    questions, bindings, text_questions = [], [], []
    for field in pending[:3]:
        title = f"{LABELS[field]}を選んでください。"
        if field == "reverse_question_count":
            default_count = DEFAULT_QUESTION_COUNTS[state["output_mode"]]
            title = f"逆質問は何問生成しますか？標準は{default_count}問です。自由入力で7問なども指定できます。"
        if field in ("company", "competitors"):
            title = ("分析する企業名または業界名を入力してください。" if field == "company"
                     else "比較する内定先の企業名を入力してください。未定なら「おまかせ」と入力できます。")
            if ui == "async":
                questions.append({"title": title})
                bindings.append({"field": field, "input": "text"})
            else:
                # The standard tool requires choices, so don't invent company names
                # or call a choice a free-text field. Ask this part in the chat.
                text_questions.append(title)
            continue

        options = options_for(field)
        narrowed = state.get(field + "_choices")
        if narrowed:
            options = [(key, label) for key, label in options if key in narrowed]
        if ui == "standard" and len(options) > 3:
            size = math.ceil(len(options) / 3)
            groups = [options[i:i + size] for i in range(0, len(options), size)]
            choices = [(" / ".join(label for _, label in group),
                        {field: group[0][0]} if len(group) == 1
                        else {field + "_choices": [key for key, _ in group]}) for group in groups]
            title = f"{LABELS[field]}の候補グループを選んでください。次に個別の項目を選べます。"
        else:
            choices = [(label, {field: key}) for key, label in options]
        binding = {"field": field, "input": "choice", "updates": dict(choices)}
        if ui == "async":
            questions.append({"title": title, "options": [label for label, _ in choices]})
            bindings.append(binding)
        elif ui == "standard":
            questions.append({
                "id": field, "header": LABELS[field], "question": title,
                "options": [{"label": label, "description": f"{label}を選択して進みます。"} for label, _ in choices],
            })
            bindings.append(binding)
        else:
            text_questions.append(title + "（" + " / ".join(label for label, _ in choices) + "）")
            bindings.append(binding)
    return {
        "status": "collecting", "state": state, "ui": ui,
        "tool": {"async": "request_user_input_async", "standard": "request_user_input", "text": None}[ui],
        "arguments": {"questions": questions} if questions else None,
        "bindings": bindings, "text_questions": text_questions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", default="{}", help="Known answers as a JSON object; no files are written")
    parser.add_argument("--ui", choices=["async", "standard", "text"], default="async")
    args = parser.parse_args()
    try:
        result = prepare_intake(json.loads(args.state), args.ui)
    except (TypeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
