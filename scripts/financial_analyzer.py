#!/usr/bin/env python3
"""
Financial, Cash Flow & Human Capital Gap Analyzer for Company Analysis Skill.

Computes and diagnoses:
1. Profitability, Growth, Efficiency & Safety Ratios
2. Cash Flow 8-Pattern Diagnosis (営業CF × 投資CF × 財務CF)
3. Employee Productivity (1人あたり売上高・営業利益)
4. Human capital inputs and limited, score-based observations (not a workplace quality verdict)
"""

import argparse
import json
import math
import sys
from typing import Dict, Optional


# Signs describe flows, not the reasons for those flows or financial health.
CF_PATTERNS = {
    (True, False, False): ("営業流入・投資/財務流出型", "営業活動は資金流入、投資活動と財務活動は資金流出です。"),
    (True, False, True): ("営業/財務流入・投資流出型", "営業活動と財務活動は資金流入、投資活動は資金流出です。"),
    (True, True, False): ("営業/投資流入・財務流出型", "営業活動と投資活動は資金流入、財務活動は資金流出です。"),
    (False, False, True): ("財務流入・営業/投資流出型", "財務活動は資金流入、営業活動と投資活動は資金流出です。"),
    (False, True, False): ("投資流入・営業/財務流出型", "投資活動は資金流入、営業活動と財務活動は資金流出です。"),
    (False, True, True): ("投資/財務流入・営業流出型", "投資活動と財務活動は資金流入、営業活動は資金流出です。"),
    (True, True, True): ("全活動資金流入型", "営業・投資・財務の各活動で資金流入です。"),
    (False, False, False): ("全活動資金流出型", "営業・投資・財務の各活動で資金流出です。"),
}


def diagnose_cash_flow(op_cf: float, inv_cf: float, fin_cf: float) -> dict:
    values = (op_cf, inv_cf, fin_cf)
    if not all(math.isfinite(value) for value in values):
        raise ValueError("CFは有限値で指定してください")
    signs = tuple("＋" if value > 0 else "−" if value < 0 else "0" for value in values)
    if 0 in values:
        label = "ゼロCFを含む（符号8分類の対象外）"
        diagnosis = "ゼロの活動には資金の純流入・純流出がなく、プラス/マイナスへ割り当てません。"
    else:
        label, diagnosis = CF_PATTERNS[tuple(value > 0 for value in values)]
    free_cf = op_cf + inv_cf
    net_cf = sum(values)
    covers_investment = None
    amount_findings = []
    if op_cf >= 0 and inv_cf < 0:
        covers_investment = op_cf >= -inv_cf
        amount_findings.append(
            "営業CFで投資CFの純流出額を賄えています。" if covers_investment
            else "営業CFだけでは投資CFの純流出額を賄えていません。"
        )
    if net_cf < 0:
        amount_findings.append("3区分CFの合計は資金純流出です。期首現預金と今後の資金需要を確認してください。")
    elif net_cf > 0:
        amount_findings.append("3区分CFの合計は資金純流入です。各区分の内訳と継続性を確認してください。")
    else:
        amount_findings.append("3区分CFの合計はゼロです。各区分の内訳を確認してください。")
    return {
        "operating_cf": op_cf,
        "investing_cf": inv_cf,
        "financing_cf": fin_cf,
        "sign_pattern": ["positive" if v > 0 else "negative" if v < 0 else "zero" for v in values],
        "free_cf": round(free_cf, 2),
        "cash_change_before_fx": round(net_cf, 2),
        "operating_cf_covers_investing_outflow": covers_investment,
        "pattern_label": f"【{label}】営業CF({signs[0]}) / 投資CF({signs[1]}) / 財務CF({signs[2]})",
        "diagnosis": diagnosis,
        "amount_findings": amount_findings,
        "liquidity_assessment": "判定不能：期首・期末現預金、返済予定、過去の推移が未入力です。",
        "limitations": "符号と金額だけでは投資・調達の目的や企業の健全性は断定できません。3区分CF合計は為替換算差額等を含まず、現預金の増減とは一致しない場合があります。",
        "interview_tip": "CF計算書の内訳と複数年の推移を確認し、公式資料で確認できた投資・調達目的だけを志望動機や質問の根拠にしてください。",
    }


def diagnose_human_capital(
    avg_age: Optional[float],
    avg_tenure: Optional[float],
    avg_salary_man: Optional[float],
    ow_overall: Optional[float],
    ow_growth20s: Optional[float],
    ow_compliance: Optional[float],
    ow_evaluation: Optional[float],
) -> dict:
    findings = []
    for label, value, unit in [
        ("平均年齢", avg_age, "歳"),
        ("平均勤続年数", avg_tenure, "年"),
        ("平均年間給与", avg_salary_man, "万円"),
    ]:
        if value is not None:
            findings.append(f"{label}: {value}{unit}（入力値）。")
    if avg_age is not None or avg_tenure is not None:
        findings.append("平均年齢・勤続年数だけでは定着率や成長機会は判定できません。採用数・離職率・従業員数の推移を確認してください。")
    if avg_salary_man is not None:
        findings.append("給与は対象年度・職種・単体/連結の範囲を揃えて比較してください。持株会社の数値かどうかも確認が必要です。")

    scores = {
        "overall": ("総合評価", ow_overall),
        "growth20s": ("20代成長環境", ow_growth20s),
        "compliance": ("法令順守意識", ow_compliance),
        "evaluation": ("人事評価の適正感", ow_evaluation),
    }
    provided = {key: value for key, (_, value) in scores.items() if value is not None}
    missing = [label for label, value in scores.values() if value is None]
    for label, value in scores.values():
        if value is not None:
            if not math.isfinite(value) or not 1 <= value <= 5:
                raise ValueError(f"{label}は1〜5の有限値で指定してください")
            band = "高め" if value >= 3.8 else "低め" if value <= 2.7 else "中間帯"
            findings.append(f"口コミの{label}: {value}/5（参考区分: {band}）。")
    if not provided:
        archetype_label = "判定不能（口コミ指標未入力）"
    elif missing:
        archetype_label = "判定保留（口コミ指標不足）"
        findings.append("未入力のため判定不能: " + "、".join(missing) + "。")
    elif ow_growth20s >= 3.8 and ow_compliance < 3.0:
        archetype_label = "成長環境と法令順守の評価差あり（要確認）"
    elif ow_compliance >= 3.8 and ow_growth20s <= 2.7:
        archetype_label = "法令順守と成長環境の評価差あり（要確認）"
    elif ow_overall >= 3.6 and min(ow_growth20s, ow_compliance, ow_evaluation) >= 3.3:
        archetype_label = "入力4指標が相対的に高め（要確認）"
    else:
        archetype_label = "入力4指標を個別確認（企業全体の良否は判定不能）"
    if provided:
        findings.append("参考区分は便宜的なしきい値（高め3.8以上、低め2.7以下）です。投稿件数・時期・職種・部署の偏りを確認し、口コミを未検証の傾向として扱ってください。")
    return {
        "organization_archetype": archetype_label,
        "provided_scores": provided,
        "missing_scores": missing,
        "findings": findings,
        "limitations": "待遇・労働時間・長期育成や企業全体の健全性は、入力された口コミ評価だけでは判定できません。公式情報とのギャップは同一時期・対象範囲の資料を別途照合してください。",
    }


def analyze_financials(args) -> dict:
    metrics = {}

    if args.revenue and args.revenue > 0:
        metrics["revenue_oku"] = args.revenue
        if args.gross_profit is not None:
            metrics["gross_margin_pct"] = round((args.gross_profit / args.revenue) * 100, 2)
        if args.operating_profit is not None:
            op_margin = round((args.operating_profit / args.revenue) * 100, 2)
            metrics["operating_margin_pct"] = op_margin
        if args.net_profit is not None:
            metrics["net_margin_pct"] = round((args.net_profit / args.revenue) * 100, 2)
        if args.rd_expense is not None:
            metrics["rd_ratio_pct"] = round((args.rd_expense / args.revenue) * 100, 2)
        if args.overseas_revenue is not None:
            metrics["overseas_ratio_pct"] = round((args.overseas_revenue / args.revenue) * 100, 2)
        if args.prev_revenue and args.prev_revenue > 0:
            yoy = round(((args.revenue - args.prev_revenue) / args.prev_revenue) * 100, 2)
            metrics["revenue_growth_yoy_pct"] = yoy
            if "operating_margin_pct" in metrics:
                metrics["rule_of_40_score"] = round(yoy + metrics["operating_margin_pct"], 2)

        if args.employees and args.employees > 0:
            # 億円 -> 万円換算 (1億円 = 10,000万円)
            rev_per_emp_man = round((args.revenue * 10000) / args.employees, 1)
            metrics["revenue_per_employee_man"] = rev_per_emp_man
            if args.operating_profit is not None:
                op_per_emp_man = round((args.operating_profit * 10000) / args.employees, 1)
                metrics["operating_profit_per_employee_man"] = op_per_emp_man

    if args.total_assets and args.total_assets > 0:
        if args.equity is not None:
            metrics["equity_ratio_pct"] = round((args.equity / args.total_assets) * 100, 2)
        if args.net_profit is not None:
            metrics["roa_pct"] = round((args.net_profit / args.total_assets) * 100, 2)

    if args.equity and args.equity > 0 and args.net_profit is not None:
        metrics["roe_pct"] = round((args.net_profit / args.equity) * 100, 2)

    cf_result = None
    if (
        args.operating_cf is not None
        and args.investing_cf is not None
        and args.financing_cf is not None
    ):
        cf_result = diagnose_cash_flow(args.operating_cf, args.investing_cf, args.financing_cf)

    hc_result = diagnose_human_capital(
        avg_age=args.avg_age,
        avg_tenure=args.avg_tenure,
        avg_salary_man=args.avg_salary,
        ow_overall=args.ow_overall,
        ow_growth20s=args.ow_growth20s,
        ow_compliance=args.ow_compliance,
        ow_evaluation=args.ow_evaluation,
    )

    commentary = []
    op_m = metrics.get("operating_margin_pct")
    if op_m is not None:
        if op_m >= 15.0:
            commentary.append(
                f"営業利益率 {op_m}%：極めて高い収益性です。強い価格決定権・高シェア・またはストック型ビジネスモデル（高い参入障壁 Moat）が存在します。"
            )
        elif op_m >= 8.0:
            commentary.append(f"営業利益率 {op_m}%：標準を上回る健全な収益力を持っています。")
        elif op_m >= 0:
            commentary.append(
                f"営業利益率 {op_m}%：利益率がやや低め、または先行投資フェーズです。中期経営計画でどのように高付加価値化・利益率改善を図る方針か確認しましょう。"
            )
        else:
            commentary.append(
                f"営業利益率 {op_m}%（営業赤字）：Jカーブの先行投資期か、一時的な業績悪化かを決算説明資料の増減要因分析で切り分けてください。"
            )

    r40 = metrics.get("rule_of_40_score")
    if r40 is not None:
        status = "優良基準（40%以上）クリア" if r40 >= 40.0 else "40%未満（成長加速または利益率改善途上）"
        commentary.append(f"Rule of 40（売上成長率＋営業利益率）：{r40}% → {status}")

    roe = metrics.get("roe_pct")
    if roe is not None:
        if roe >= 10.0:
            commentary.append(f"ROE {roe}%：グローバル投資家が求める8〜10%水準を上回る高い資本効率です。")
        else:
            commentary.append(f"ROE {roe}%：資本効率の改善（PBR1倍割れ対策やROIC経営）が経営課題になっている可能性が高いです。")

    return {
        "company": args.company or "対象企業",
        "metrics": metrics,
        "financial_commentary": commentary,
        "cash_flow_diagnosis": cf_result,
        "human_capital_diagnosis": hc_result,
    }


def format_markdown(result: dict) -> str:
    m = result["metrics"]
    lines = [
        f"# 📈 財務・キャッシュフロー・人的資本 総合診断レポート：{result['company']}",
        "",
        "## 1. 主要財務指標・生産性KPI",
    ]
    if not m:
        lines.append("- （財務数値が未入力です）")
    else:
        label_map = {
            "revenue_oku": ("売上高", "億円"),
            "revenue_growth_yoy_pct": ("売上高成長率 (YoY)", "%"),
            "gross_margin_pct": ("売上総利益率 (粗利率)", "%"),
            "operating_margin_pct": ("営業利益率", "%"),
            "net_margin_pct": ("当期純利益率", "%"),
            "roe_pct": ("ROE (自己資本当期純利益率)", "%"),
            "roa_pct": ("ROA (総資産当期純利益率)", "%"),
            "equity_ratio_pct": ("自己資本比率", "%"),
            "rd_ratio_pct": ("研究開発費 (R&D) 売上比率", "%"),
            "overseas_ratio_pct": ("海外売上高比率", "%"),
            "rule_of_40_score": ("Rule of 40 スコア", "%"),
            "revenue_per_employee_man": ("1人あたり売上高", "万円/人"),
            "operating_profit_per_employee_man": ("1人あたり営業利益", "万円/人"),
        }
        for key, (label, unit) in label_map.items():
            if key in m:
                lines.append(f"- **{label}**: `{m[key]} {unit}`")

    if result["financial_commentary"]:
        lines.append("\n### 💡 財務指標からの戦略的示唆")
        for c in result["financial_commentary"]:
            lines.append(f"- {c}")

    cf = result["cash_flow_diagnosis"]
    if cf:
        lines.extend([
            "",
            "## 2. キャッシュフロー8パターン診断",
            f"- **営業CF**: `{cf['operating_cf']} 億円` / **投資CF**: `{cf['investing_cf']} 億円` / **財務CF**: `{cf['financing_cf']} 億円` （**FCF**: `{cf['free_cf']} 億円`）",
            f"- **診断タイプ**: **{cf['pattern_label']}**",
            f"- **資金の流入/流出**: {cf['diagnosis']}",
            f"- **3区分CF合計（為替換算差額等を除く）**: `{cf['cash_change_before_fx']} 億円`",
            *[f"- {finding}" for finding in cf['amount_findings']],
            f"- **資金繰りの健全性**: {cf['liquidity_assessment']}",
            f"- **判定の限界**: {cf['limitations']}",
            f"- **🎯 面接・志望動機での活用法**: {cf['interview_tip']}",
        ])

    hc = result["human_capital_diagnosis"]
    if hc and hc["findings"]:
        lines.extend([
            "",
            "## 3. 人的資本・口コミ（OpenWork等）クロスギャップ診断",
            f"- **組織タイプ判定**: **{hc['organization_archetype']}**",
        ])
        for f in hc["findings"]:
            lines.append(f"- {f}")
        lines.append(f"- **判定の限界**: {hc['limitations']}")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Company Financial & Human Capital Analyzer")
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument("--revenue", type=float, help="Current revenue (in 億円)")
    parser.add_argument("--prev-revenue", type=float, help="Previous year revenue (in 億円)")
    parser.add_argument("--gross-profit", type=float, help="Gross profit (売上総利益 in 億円)")
    parser.add_argument("--operating-profit", type=float, help="Operating profit (営業利益 in 億円)")
    parser.add_argument("--net-profit", type=float, help="Net profit (当期純利益 in 億円)")
    parser.add_argument("--total-assets", type=float, help="Total assets (総資産 in 億円)")
    parser.add_argument("--equity", type=float, help="Shareholders equity (自己資本 in 億円)")
    parser.add_argument("--rd-expense", type=float, help="R&D expense (研究開発費 in 億円)")
    parser.add_argument("--overseas-revenue", type=float, help="Overseas revenue (海外売上高 in 億円)")
    parser.add_argument("--employees", type=int, help="Number of employees (連結または単体従業員数)")
    parser.add_argument("--operating-cf", type=float, help="Operating cash flow (営業CF in 億円)")
    parser.add_argument("--investing-cf", type=float, help="Investing cash flow (投資CF in 億円)")
    parser.add_argument("--financing-cf", type=float, help="Financing cash flow (財務CF in 億円)")
    parser.add_argument("--avg-age", type=float, help="Average employee age (平均年齢)")
    parser.add_argument("--avg-tenure", type=float, help="Average years of tenure (平均勤続年数)")
    parser.add_argument("--avg-salary", type=float, help="Average annual salary in 万円 (平均年間給与)")
    parser.add_argument("--ow-overall", type=float, help="OpenWork overall score (e.g. 3.8)")
    parser.add_argument("--ow-growth20s", type=float, help="OpenWork 20s growth score")
    parser.add_argument("--ow-compliance", type=float, help="OpenWork compliance score")
    parser.add_argument("--ow-evaluation", type=float, help="OpenWork evaluation fairness score")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")

    args = parser.parse_args()
    try:
        res = analyze_financials(args)
    except ValueError as exc:
        parser.error(str(exc))
    if args.format == "json":
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(res))


if __name__ == "__main__":
    main()
