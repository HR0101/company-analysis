#!/usr/bin/env python3
"""
Financial, Cash Flow & Human Capital Gap Analyzer for Company Analysis Skill.

Computes and diagnoses:
1. Profitability, Growth, Efficiency & Safety Ratios (with industry-aware commentary)
2. Cash Flow 8-Pattern Diagnosis (営業CF × 投資CF × 財務CF)
3. Employee Productivity (1人あたり売上高・営業利益)
4. Human Capital & OpenWork Radar Gap Diagnosis (真のホワイト vs ゆるブラック vs 若手ハードワーク型)
"""

import argparse
import json
import sys
from typing import Dict, Optional


CF_PATTERNS = {
    (True, False, False): {
        "label": "【王道・優良成長型】営業CF(＋) / 投資CF(−) / 財務CF(−)",
        "diagnosis": "本業で潤沢なキャッシュを稼ぎ、その範囲内で将来への設備・成長投資を行い、借入金返済や株主還元（配当・自社株買い）も進められている最も健全なキャッシュフロー構造です。",
        "interview_tip": "『盤石な収益基盤（営業CF）を原資に、中期経営計画の〇〇領域へ継続投資できている点に安定性と成長性の両立を感じる』と志望動機で語ると説得力が増します。",
    },
    (True, False, True): {
        "label": "【積極拡大・勝負投資型】営業CF(＋) / 投資CF(−) / 財務CF(＋)",
        "diagnosis": "本業でしっかり稼ぎつつも、それ以上に大型M&Aや新工場・DX投資などの勝負に出るため、外部から資金調達（借入・社債・増資）を行ってアクセルを踏んでいるフェーズです。",
        "interview_tip": "大型投資やM&Aの対象領域を特定し、『今まさに御社が社運を賭けて投資している〇〇領域の立ち上げ・PMIに貢献したい』と切り込むのが有効です。",
    },
    (True, True, False): {
        "label": "【事業再編・選択と集中型】営業CF(＋) / 投資CF(＋) / 財務CF(−)",
        "diagnosis": "本業で稼ぎつつ、非中核事業や保有資産・政策保有株を売却してキャッシュを作り、借入金の圧縮や株主還元・ポートフォリオ転換を進めている構造改革フェーズです。",
        "interview_tip": "『ROIC経営や事業ポートフォリオの選択と集中を進め、高収益なコア事業へ経営資源を再配分している変革期』として捉え、逆質問で今後の注力領域を問うのが効果的です。",
    },
    (False, False, True): {
        "label": "【先行投資・Jカーブ成長型】営業CF(−) / 投資CF(−) / 財務CF(＋)",
        "diagnosis": "グロース期のスタートアップやSaaS企業に典型的な形で、ベンチャーキャピタルや市場からの資金調達（財務CF＋）を原資に、プロダクト開発と顧客獲得（S&M）へ先行投資してシェアを奪いに行っている状態です。",
        "interview_tip": "黒字転換のタイムラインやARR成長率・ユニットエコノミクス（LTV/CAC）を確認し、『シェア拡大の勝負フェーズにおいて〇〇で成長を牽引したい』と語ると刺さります。",
    },
    (False, True, False): {
        "label": "【リストラ・資産切り売り注意型】営業CF(−) / 投資CF(＋) / 財務CF(−)",
        "diagnosis": "本業が赤字でキャッシュが流出する中、資産や事業の売却で得た資金で借入金を返済している状態です。一時的な特損要因か構造的な衰退かを慎重に見極める必要があります。",
        "interview_tip": "有価証券報告書の『対処すべき課題』と再生計画を精査し、構造改革の具体策を確認してください。",
    },
    (False, True, True): {
        "label": "【防衛・資金確保型】営業CF(−) / 投資CF(＋) / 財務CF(＋)",
        "diagnosis": "本業のキャッシュ流出を補うため、資産売却と追加借入・増資の両方で手元流動性を確保している緊急度の高いフェーズです。",
        "interview_tip": "直近の業績悪化が一過性（市況・特損等）か構造的かを決算説明資料で必ず確認してください。",
    },
    (True, True, True): {
        "label": "【超大型案件待機・手元資金積み増し型】営業CF(＋) / 投資CF(＋) / 財務CF(＋)",
        "diagnosis": "本業・資産売却・資金調達のすべてでキャッシュを積み上げており、近い将来の大型M&Aや巨額投資に備えて手元資金を厚くしているケースが多いです。",
        "interview_tip": "中期経営計画のキャッシュアロケーションを確認し、積み上げた資金を今後どこへ投下する方針かを逆質問で聞くのが有効です。",
    },
    (False, False, False): {
        "label": "【内部留保取り崩し・過渡期型】営業CF(−) / 投資CF(−) / 財務CF(−)",
        "diagnosis": "過去に蓄積した豊富な現預金を取り崩して投資と返済・還元を行っている状態です。運転資本の期ズレ（売掛金・棚卸資産の一時的増加）で一時的に営業CFがマイナスになった優良企業でも発生します。",
        "interview_tip": "単年だけでなく過去3〜5年の営業CF推移（IR BANK等）を確認し、一時的な運転資本増加かどうかを見極めてください。",
    },
}


def diagnose_cash_flow(op_cf: float, inv_cf: float, fin_cf: float) -> dict:
    key = (op_cf >= 0, inv_cf >= 0, fin_cf >= 0)
    info = CF_PATTERNS[key]
    free_cf = op_cf + inv_cf
    return {
        "operating_cf": op_cf,
        "investing_cf": inv_cf,
        "financing_cf": fin_cf,
        "free_cf": round(free_cf, 2),
        "pattern_label": info["label"],
        "diagnosis": info["diagnosis"],
        "interview_tip": info["interview_tip"],
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
    archetype_label = "標準バランス型"

    if avg_age is not None and avg_tenure is not None:
        if avg_tenure >= 14.0 and avg_age >= 38.0:
            findings.append(
                f"平均年齢{avg_age}歳・平均勤続{avg_tenure}年：長期定着率が極めて高い安定組織です。一方で年功序列感や若手の抜擢機会について現場社員に確認すると解像度が上がります。"
            )
        elif avg_tenure <= 4.5 and avg_age <= 33.0:
            findings.append(
                f"平均年齢{avg_age}歳・平均勤続{avg_tenure}年：若手が主力で急拡大中の組織、または人材の流動性（入れ替わり）が激しい環境です。従業員数が毎年増加しているための勤続年数低下か、離職によるものかを過去3年の有報で照合してください。"
            )
        else:
            findings.append(
                f"平均年齢{avg_age}歳・平均勤続{avg_tenure}年：新陳代謝と定着のバランスが取れた組織構成です。"
            )

    if avg_salary_man is not None:
        if avg_salary_man >= 900:
            findings.append(
                f"平均年間給与 約{avg_salary_man:.0f}万円：国内トップクラスの高水準です（※持株会社単体の数字でないかだけ念のため確認してください）。"
            )
        elif avg_salary_man >= 650:
            findings.append(f"平均年間給与 約{avg_salary_man:.0f}万円：上場企業平均を上回る良好な待遇水準です。")
        else:
            findings.append(
                f"平均年間給与 約{avg_salary_man:.0f}万円：住宅手当・借上社宅等の福利厚生（有報に含まれない実質報酬）や昇給カーブをオファー面談等で確認すると安心です。"
            )

    if ow_overall is not None:
        if (
            ow_growth20s is not None
            and ow_compliance is not None
            and ow_growth20s >= 3.8
            and ow_compliance < 3.0
        ):
            archetype_label = "【若手ハードワーク・早期成長特化型】"
            findings.append(
                "OpenWork診断：『20代成長環境』が突出して高い一方、コンプライアンスや長期育成が低めです。20代で圧倒的な裁量と市場価値を得る環境としては魅力的ですが、ハードワーク耐性が求められます。"
            )
        elif (
            ow_growth20s is not None
            and ow_compliance is not None
            and ow_compliance >= 3.8
            and ow_growth20s <= 2.7
        ):
            archetype_label = "【ゆるブラック（ぬるま湯・成長停滞）注意型】"
            findings.append(
                "OpenWork診断：法令順守や働きやすさは非常に高い一方、『20代成長環境』『人事評価の適正感』が低めです。ワークライフバランスは良好ですが、自ら主体的に動く部署を選ばないと市場価値が伸び悩む（いわゆる『ゆるブラック』）リスクに注意してください。"
            )
        elif ow_overall >= 3.6 and (ow_compliance is None or ow_compliance >= 3.3):
            archetype_label = "【真のホワイト・高エンゲージメント優良型】"
            findings.append(
                f"OpenWork診断（総合{ow_overall}）：成長機会とコンプライアンス・待遇のバランスが高水準で両立している優良組織です。"
            )
        elif ow_overall < 2.9:
            archetype_label = "【公式発表と現場体感のギャップ注意型】"
            findings.append(
                f"OpenWork診断（総合{ow_overall}）：現場の不満が蓄積している可能性があります。統合報告書や採用HPのアピールだけでなく、退職検討理由の共通項（評価制度・残業実態・部署間格差）を必ず点検してください。"
            )

    return {
        "organization_archetype": archetype_label,
        "findings": findings,
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
            f"- **経営状態の解釈**: {cf['diagnosis']}",
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
    res = analyze_financials(args)
    if args.format == "json":
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(res))


if __name__ == "__main__":
    main()
