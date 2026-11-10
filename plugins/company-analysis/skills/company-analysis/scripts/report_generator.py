#!/usr/bin/env python3
"""
Customized Company Analysis & Selection Strategy Report Generator.

Generates structured Markdown templates / worksheets tailored to the chosen:
- Industry pattern
- Job role pattern
- Selection stage / interview round pattern
- Candidate type
- Company archetype
- Report mode: 'full' (default), 'cheatsheet' (5-min pre-interview sheet), or 'offer-comparison'
"""

import argparse
from pathlib import Path
import re
import sys
import unicodedata

# Ensure sibling import works regardless of current working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pattern_selector import (
    ARCHETYPE_PATTERNS,
    CANDIDATE_PATTERNS,
    INDUSTRY_PATTERNS,
    ROLE_PATTERNS,
    STAGE_PATTERNS,
    build_blueprint,
    resolve_pattern,
)


DEFAULT_QUESTION_COUNTS = {"full": 100, "cheatsheet": 100}

QUESTION_THEMES = [
    "希望職種のミッション", "事業戦略・投資", "顧客・競争優位", "仕事の進め方・裁量",
    "チーム・部署間の連携", "成果・評価制度", "育成・キャリア", "組織文化・価値観",
    "働き方・支援制度", "入社後の期待・立ち上がり",
]
QUESTION_ANGLES = [
    "{theme}について、現在特に大切にされている目標は何でしょうか？",
    "{theme}の現状が分かる具体的な事例を教えていただけますか？",
    "{theme}を進める上で、現場で難しさを感じる点は何でしょうか？",
    "{theme}で複数の選択肢があるとき、どのような基準で優先順位を決めますか？",
    "{theme}の改善や進捗を、どのような指標・情報から判断されていますか？",
    "{theme}で関係者の意見が異なる場合、どのように合意をつくりますか？",
    "{theme}について、これまでの経験から見直した取り組みはありますか？",
    "{theme}に関して、今後変えていきたいことはありますか？",
    "{theme}に関して、社員からの提案を取り入れる機会はどのように設けられていますか？",
    "{theme}について、新しく入社する人が事前に理解しておくとよいことは何でしょうか？",
]


def parse_question_count(value):
    if value is None or value in ("auto", "標準", "おまかせ"):
        return "auto"
    if isinstance(value, bool) or not isinstance(value, (str, int)):
        raise ValueError("逆質問の件数は0以上の整数で指定してください")
    text = unicodedata.normalize("NFKC", str(value)).strip()
    if text in ("不要", "不要(0問)"):
        return 0
    if not re.fullmatch(r"[0-9]+(?:問)?", text):
        raise ValueError("逆質問の件数は0以上の整数で指定してください（例: 7、7問）")
    return int(text.removesuffix("問"))


def resolve_question_count(value, mode):
    count = parse_question_count(value)
    return DEFAULT_QUESTION_COUNTS[mode] if count == "auto" else count


def reverse_question_list(bp, count):
    """Make worksheet slots; company-specific evidence is filled in by the skill."""
    grouped = [[angle.format(theme=theme) for angle in QUESTION_ANGLES] for theme in QUESTION_THEMES]
    for i, question in enumerate(bp["step3_role_analysis"]["role_reverse_questions"][:2]):
        grouped[0][i] = question
    if count >= 100:
        entries = [(theme, q) for theme, group in zip(QUESTION_THEMES, grouped) for q in group]
    else:
        entries = [(theme, group[i]) for i in range(10) for theme, group in zip(QUESTION_THEMES, grouped)]
    questions = [f"【{theme}】{question}" for theme, question in entries]
    while len(questions) < count:
        questions.append(f"【追加テーマ{len(questions) + 1}の確認済み事実】＋【重複しない現場仮説】＋【この面接官に確認する問い】を記入。")
    return "\n".join(f"{i}. 「{question}」" for i, question in enumerate(questions[:count], 1))


def self_introduction_section(text=None, heading="### ③"):
    if text is None:
        body = (
            "（会話履歴・提供済みの経歴資料で確認できる所属、経験・実績、強みをもとに、"
            "約1分・250〜350字を目安とする自己紹介原稿を記入。氏名・経歴・数値を創作しない。"
            "情報不足なら必要な点だけ確認する。）"
        )
    else:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("自己紹介原稿は空でない文字列で指定してください")
        body = text.strip()
    return f"{heading} 自己紹介（約1分）\n{body}"


def generate_full_report(bp: dict, reverse_question_count=None, self_introduction=None) -> str:
    company = bp["target_company"]
    comps = bp["competitors"]
    comp_a = comps[0] if len(comps) > 0 else "競合A社"
    comp_b = comps[1] if len(comps) > 1 else "競合B社"
    sp = bp["selected_patterns"]
    ind = bp["step2_industry_analysis"]
    role = bp["step3_role_analysis"]
    stage = bp["step4_stage_strategy"]

    kpi_rows = "\n".join(
        [f"| {kpi} | （調査値を記入） | （競合・業界水準） | （強み・課題の示唆） |" for kpi in ind["key_kpis"]]
    )
    comp_rows = "\n".join(
        [f"| **{axis}** | | | |" for axis in ind["competitor_axes"]]
    )
    role_checks = "\n".join(
        [f"- [ ] {chk}" for chk in role["operational_checkpoints"]]
    )
    primary_srcs = "\n".join(
        [f"- [ ] {src}" for src in bp["step1_primary_sources"]]
    )
    pass_strats = "\n".join(
        [f"- {s}" for s in stage["pass_strategy"]]
    )
    count = resolve_question_count(reverse_question_count, "full")
    reverse_section = (
        f"### ⑤ 仮説検証型・逆質問リスト（{count}問：一次情報の事実＋現場仮説＋問い）\n"
        + reverse_question_list(bp, count)
    ) if count else ""

    return f"""# 📊 【企業分析＆選考突破マスターシート】{company}

- **設定パターン**:
  - **業界**: `{sp['industry']['id']}` ({sp['industry']['name']})
  - **希望職種**: `{sp['role']['id']}` ({sp['role']['name']})
  - **選考フェーズ**: `{sp['stage']['id']}` ({sp['stage']['name']})
  - **応募区分**: `{sp['candidate']['id']}` ({sp['candidate']['name']})
  - **企業タイプ**: `{sp['archetype']['id']}` ({sp['archetype']['name']})

---

## 0. 一次情報チェックリスト（最初に当たるべき情報源）
{primary_srcs}

---

## 1. エグゼクティブサマリー（3行で語る{company}の本質）
- **現在の収益の柱（何で稼いでいるか）**: 
- **最大の競争優位性・参入障壁（なぜ勝てているか / Moat）**: 
- **今後3〜5年の注力方向性（中期経営計画・成長ドライバー）**: 

---

## 2. ビジネスモデル解剖（4W1H ＋ 業界固有構造）
| 分析軸 | {company}の構造・特徴 | 選考（志望動機・逆質問）への示唆 |
| :--- | :--- | :--- |
| **Who（主要顧客・意思決定者）** | | |
| **What（提供価値・解決する不）** | | |
| **How（商流・提供チャネル・技術）** | | |
| **How Much（課金モデル：ストック vs フロー）** | | |
| **Moat（他社が模倣できない参入障壁）** | | |

### 業界特有のビジネスモデル着眼点（{sp['industry']['name']}）
{chr(10).join([f"- {b}" for b in ind['business_model_focus']])}

---

## 3. 定量・財務・業界特化KPI分析
| チェック指標 | {company}の実績・推移 | 業界目安・{comp_a}水準 | 戦略的解釈・面接での語り方 |
| :--- | :--- | :--- | :--- |
| **売上高 / YoY成長率** | | | |
| **営業利益 / 営業利益率** | | | |
| **ROE / 自己資本比率 / CFパターン** | | | |
{kpi_rows}
| **平均年間給与 / 平均年齢 / 平均勤続年数** | | | |

---

## 4. 競合他社比較マトリクス（「なぜ他社ではなく{company}か」の根拠）
| 比較軸 | **{company}（志望企業）** | **{comp_a}** | **{comp_b}** |
| :--- | :--- | :--- | :--- |
| **主力事業・強みセグメント** | | | |
| **中長期戦略・投資の方向性** | | | |
| **社風・カルチャー・人材育成観** | | | |
{comp_rows}

### 💡 競合差別化の結論フレーズ（Why {company}）
> 「{sp['industry']['name']}の中でも、{comp_a}は〇〇、{comp_b}は△△に強みを持つ一方、御社は【独自の強み・戦略】という明確な違いがあります。私の【原体験・キャリア軸】を実現する上で、御社の環境こそが最もフィットすると確信しています。」

---

## 5. 希望職種（{sp['role']['name']}）の業務解像度＆課題仮説
### 必ず調べるべき職種別5大チェックポイント
{role_checks}

### クロスSWOTから導く「{sp['role']['name']}の現場課題仮説」
- **全社の中計・事業リスクから見た当部門のミッション**: 
- **現場がいま直面しているボトルネック仮説**: 
- **自分が証明すべき再現性（Why Me）**:
  - {role['reproducibility_proof']}

---

## 6. 組織文化・人的資本ギャップ診断（統合報告書 × OpenWork突合）
- **企業理念（VMV）・カルチャーデックの要点**: 
- **公式開示データ（有給取得率・残業時間・離職率・女性管理職比率等）**: 
- **入力済みの口コミ指標・投稿時期・件数・職種/部署**:
- **確認済みの違い・未検証の仮説・追加確認事項**:

---

## 7. 【{sp['stage']['name']}特化】選考突破アウトプット

### ① 面接官プロファイルと合格条件
- **想定される評価者**: {stage['interviewer_persona']}
- **このフェーズの合格の核心**: {stage['core_objective']}
- **応募区分（{sp['candidate']['name']}）での注意点**: {bp['step5_candidate_adjustment']}

### ② 突破のための具体的戦術
{pass_strats}

{self_introduction_section(self_introduction)}

### ④ 志望動機ドラフト（結論ファースト・1分話せる350字版）
1. **成し遂げたい軸（結論）**: 
2. **原体験・背景**: 
3. **なぜこの業界×なぜ{company}か（競合比較）**: 
4. **なぜ{sp['role']['name']}か×入社後の貢献（再現性）**: 

{reverse_section}
"""


def generate_cheatsheet(bp: dict, reverse_question_count=None, self_introduction=None) -> str:
    company = bp["target_company"]
    comps = bp["competitors"]
    comp_a = comps[0] if len(comps) > 0 else "競合A社"
    sp = bp["selected_patterns"]
    role = bp["step3_role_analysis"]
    stage = bp["step4_stage_strategy"]
    count = resolve_question_count(reverse_question_count, "cheatsheet")
    question_heading = "## 付録. テーマ別の逆質問集" if count >= 100 else "## 3. 面接で確認したい逆質問"
    reverse_section = (
        f"{question_heading}（{count}問）\n" + reverse_question_list(bp, count)
    ) if count else ""
    priority_section = "## 3. 当日優先する質問\n（付録から面接官に合う質問番号を3〜5件選び、理由を記入。）\n\n---\n\n" if count >= 100 else ""

    return f"""# ⚡ 【面接直前5分チートシート】{company} × {sp['stage']['name']}

- **志望職種**: {sp['role']['name']} / **区分**: {sp['candidate']['name']}
- **今日の面接官**: **{stage['interviewer_persona']}**
- **今日の最重要ゴール**: **{stage['core_objective']}**

---

{self_introduction_section(self_introduction, "## 0.")}

---

## 1. 第一声（30〜45秒）で伝える志望動機の核
- **結論（軸）**: 「私が御社を志望する理由は、〇〇を通じて△△を実現したいからです。」
- **なぜ{company}か（対{comp_a}差別化）**: 「同業の{comp_a}と比較しても、御社は【独自の強み・中計の戦略】に特徴があり、私の目指す方向性と最も一致しています。」
- **どう貢献するか（{sp['role']['name']}の再現性）**:
  - {role['reproducibility_proof']}

---

## 2. このフェーズ（{sp['stage']['name']}）の鉄則チェック
{chr(10).join([f"- [x] {s}" for s in stage['pass_strategy']])}

---

{priority_section}{reverse_section}
"""


def generate_offer_comparison(bp: dict) -> str:
    company = bp["target_company"]
    comps = bp["competitors"]
    comp_a = comps[0] if len(comps) > 0 else "比較企業A社"
    comp_b = comps[1] if len(comps) > 1 else "比較企業B社"

    return f"""# ⚖️ 【内定比較・オファー面談意思決定シート】{company} vs 他社内定

## 1. 5軸100点満点・客観スコアリングマトリクス
| 評価軸（各20点満点） | 具体的なチェック項目 | **{company}** | **{comp_a}** | **{comp_b}** |
| :--- | :--- | :---: | :---: | :---: |
| **① キャリア市場価値（20点）** | 3〜5年後にどんな職務経歴書が書けるか？他社でも通用する専門性・ポータブルスキルが身につくか？ | /20 | /20 | /20 |
| **② 事業・財務の将来性（20点）** | 市場は成長しているか？参入障壁（Moat）と営業利益率・営業CF創出力は盤石か？ | /20 | /20 | /20 |
| **③ 業務内容・裁量・配属（20点）** | 希望職種・初期配属の確約度合いは高いか？若手のうちから意思決定の場に関われるか？ | /20 | /20 | /20 |
| **④ 組織文化・健全性（20点）** | 統合報告書とOpenWork等の口コミに乖離はないか？一緒に働く社員を尊敬できるか？ | /20 | /20 | /20 |
| **⑤ 実質総報酬・働き方（20点）** | 基本給＋賞与＋住宅補助/福利厚生−みなし残業時間の実質時給、リモート・柔軟性は納得できるか？ | /20 | /20 | /20 |
| **合計スコア（100点満点）** | **感情や知名度バイアスを除いた総合点** | **/100** | **/100** | **/100** |

---

## 2. オファー面談で必ず確認すべき質問リスト
- [ ] **初期配属とミッション**: 「入社後最初の半年間〜1年間で期待されている具体的な目標（KPI・状態目標）を教えていただけますか？」
- [ ] **評価と昇給の仕組み**: 「半期・通期の評価はどのような基準で行われ、グレード昇格にはどのような実績が求められますか？」
- [ ] **実質報酬の内訳**: 「提示いただいた理論年収に含まれる固定残業時間数、過去3年間の平均賞与支給月数、住宅手当・福利厚生の適用条件を確認させてください。」
- [ ] **チームの現状課題**: 「現在配属予定のチームが抱えている最大の課題と、今回私がジョインすることで最も解決を期待されているポイントは何でしょうか？」
"""


def main():
    parser = argparse.ArgumentParser(description="Company Analysis Report & Worksheet Generator")
    parser.add_argument("--company", default="対象企業", help="Target company name")
    parser.add_argument("--industry", default="it-saas-web", help="Industry pattern ID or keyword")
    parser.add_argument("--role", default="sales-cs", help="Job role pattern ID or keyword")
    parser.add_argument("--stage", default="first-interview", help="Selection stage pattern ID or keyword")
    parser.add_argument("--candidate", default="new-grad", help="Candidate type")
    parser.add_argument("--archetype", default="listed-enterprise", help="Company archetype")
    parser.add_argument("--competitors", default="", help="Comma-separated competitor names")
    parser.add_argument(
        "--mode",
        choices=["full", "cheatsheet", "offer-comparison"],
        default="full",
        help="Report mode: full, cheatsheet, or offer-comparison",
    )
    parser.add_argument("--output", default="", help="Optional file path to save the generated Markdown")
    parser.add_argument("--reverse-question-count", default="auto", help="逆質問の件数。0で省略、未指定は100問（full / cheatsheet共通）")
    parser.add_argument("--self-introduction-file", type=Path, help="会話履歴から作成した約1分の自己紹介原稿（UTF-8）。未指定は記入欄のみ")

    args = parser.parse_args()

    try:
        ind_key = resolve_pattern(args.industry, INDUSTRY_PATTERNS, "it-saas-web")
        role_key = resolve_pattern(args.role, ROLE_PATTERNS, "sales-cs")
        stage_key = resolve_pattern(args.stage, STAGE_PATTERNS, "first-interview")
        cand_key = resolve_pattern(args.candidate, CANDIDATE_PATTERNS, "new-grad")
        arch_key = resolve_pattern(args.archetype, ARCHETYPE_PATTERNS, "listed-enterprise")
    except ValueError as exc:
        parser.error(str(exc))
    try:
        question_count = parse_question_count(args.reverse_question_count)
    except ValueError as exc:
        parser.error(str(exc))
    offer_report = args.mode != "cheatsheet" and (args.mode == "offer-comparison" or stage_key == "offer-comparison")
    if offer_report and question_count != "auto":
        parser.error("--reverse-question-countはフル版・チートシート向けです。内定比較の確認質問とは別に扱います")
    if offer_report and args.self_introduction_file:
        parser.error("--self-introduction-fileはフル版・チートシート向けです")
    self_introduction = None
    if args.self_introduction_file:
        try:
            self_introduction = args.self_introduction_file.read_text(encoding="utf-8").strip()
            if not self_introduction:
                raise ValueError("自己紹介原稿が空です")
        except (OSError, ValueError) as exc:
            parser.error(str(exc))
    comps = [c.strip() for c in args.competitors.split(",") if c.strip()]

    bp = build_blueprint(
        company=args.company,
        industry_key=ind_key,
        role_key=role_key,
        stage_key=stage_key,
        candidate_key=cand_key,
        archetype_key=arch_key,
        competitors=comps,
    )

    if args.mode == "cheatsheet":
        md = generate_cheatsheet(bp, question_count, self_introduction)
    elif args.mode == "offer-comparison" or stage_key == "offer-comparison":
        md = generate_offer_comparison(bp)
    else:
        md = generate_full_report(bp, question_count, self_introduction)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"[OK] Saved report to {out_path}")
    else:
        print(md)


if __name__ == "__main__":
    main()
