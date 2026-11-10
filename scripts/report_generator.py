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


DEFAULT_QUESTION_COUNTS = {"full": 10, "cheatsheet": 10}
DEFAULT_INTERVIEW_QUESTION_COUNTS = {"full": 100, "cheatsheet": 100}

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
        raise ValueError("質問の件数は0以上の整数で指定してください")
    text = unicodedata.normalize("NFKC", str(value)).strip()
    if text in ("不要", "不要(0問)"):
        return 0
    if not re.fullmatch(r"[0-9]+(?:問)?", text):
        raise ValueError("質問の件数は0以上の整数で指定してください（例: 7、7問）")
    return int(text.removesuffix("問"))


def resolve_question_count(value, mode):
    count = parse_question_count(value)
    return DEFAULT_QUESTION_COUNTS[mode] if count == "auto" else count


def resolve_interview_question_count(value, mode):
    count = parse_question_count(value)
    return DEFAULT_INTERVIEW_QUESTION_COUNTS[mode] if count == "auto" else count


INTERVIEW_QUESTIONS = {
    "経歴・自己紹介": [
        "1分程度で自己紹介をお願いします。",
        "これまでの経験のうち、今回の応募に最も関連するものを教えてください。",
        "現在取り組んでいる仕事・研究・学習の内容を、専門外の人にも分かるように説明してください。",
        "ご自身の強みを具体的な経験とともに教えてください。",
        "ご自身の課題や弱みと、それに対する取り組みを教えてください。",
        "周囲からどのような人だと評価されていますか？",
        "これまでの経験に共通する、ご自身らしい行動を教えてください。",
        "所属組織やチームの中で、どのような役割を担ってきましたか？",
        "経歴の中で方向性を変えた経験があれば、その背景を教えてください。",
        "応募書類に書ききれなかった、ご自身について伝えたいことはありますか？",
    ],
    "志望動機・企業理解": [
        "当社を志望する理由を教えてください。",
        "なぜこの業界に関心を持ったのですか？",
        "同業他社と比べて、当社のどの点に魅力を感じていますか？",
        "当社の主な顧客と提供価値をどのように理解していますか？",
        "当社の収益構造について、ご自身の言葉で説明してください。",
        "当社の事業やサービスで、特に関心のあるものは何ですか？",
        "当社の直近の取り組みの中で、印象に残ったものを教えてください。",
        "当社が今後向き合うべき課題を、根拠とともに教えてください。",
        "当社の理念や価値観と、ご自身の経験が重なる点はありますか？",
        "当社への理解を深めるために、どのような情報を調べましたか？",
    ],
    "希望職種・専門性": [
        "なぜ{role}を希望しているのですか？",
        "{role}で期待される役割をどのように理解していますか？",
        "この職種に生かせる専門知識やスキルを、経験とともに説明してください。",
        "得意な業務や領域と、今後学ぶ必要がある領域を教えてください。",
        "専門的な課題を解決する際、どのように情報を集めますか？",
        "複数の手法や技術から一つを選んだ経験と、その判断理由を教えてください。",
        "ご自身の専門性を、顧客や事業の価値にどうつなげられますか？",
        "品質・納期・コストが両立しないとき、どのように判断しますか？",
        "専門外の人と仕事を進める際、説明や認識合わせで工夫していることは何ですか？",
        "この職種の変化に対応するため、最近学んでいることを教えてください。",
    ],
    "成果・課題解決": [
        "これまでに最も力を入れて取り組んだことを教えてください。",
        "その取り組みでは、どのような目標を設定しましたか？",
        "課題を特定した根拠やデータを教えてください。",
        "その取り組みで、ご自身が担当した範囲を明確にしてください。",
        "他の選択肢ではなく、その方法を選んだ理由は何ですか？",
        "実行する中で最も大きかった障害と、乗り越え方を教えてください。",
        "成果はどのように測定・確認しましたか？",
        "チームの成果と、ご自身の貢献を分けて説明してください。",
        "その成果を、別の環境でも再現するために必要な条件は何ですか？",
        "同じ取り組みをもう一度行うなら、どこを改善しますか？",
    ],
    "協働・リーダーシップ": [
        "チームで成果を出した経験を教えてください。",
        "意見が対立した場面で、どのように対応しましたか？",
        "立場の異なる関係者と合意をつくった経験はありますか？",
        "役職や権限がない中で、周囲に働きかけた経験を教えてください。",
        "相手から協力を得るために、どのような準備をしましたか？",
        "チームの進捗が遅れているとき、ご自身ならどのように動きますか？",
        "他の人に仕事を任せるとき、何を共有し、何を確認しますか？",
        "他者からのフィードバックを受けて行動を変えた経験を教えてください。",
        "他者を支援・育成した経験があれば、工夫したことを教えてください。",
        "チームの目標と自分の目標が異なるとき、どのように調整しますか？",
    ],
    "失敗・学習": [
        "これまでの失敗経験と、そこから学んだことを教えてください。",
        "期待された結果に届かなかったとき、どのように原因を調べましたか？",
        "自分の判断が誤っていたと気づいた経験はありますか？",
        "問題を周囲に報告するタイミングを、どのように判断していますか？",
        "同じ失敗を繰り返さないために、仕組みを変えた経験を教えてください。",
        "未経験の課題に取り組むとき、最初に何をしますか？",
        "短期間で新しい知識やスキルを身につけた経験を教えてください。",
        "学んだことを実践して、結果を確かめた経験はありますか？",
        "困ったときに自分で調べる範囲と、人に相談する範囲をどう分けますか？",
        "最近、ご自身の考え方が変わった出来事を教えてください。",
    ],
    "価値観・判断": [
        "仕事や研究を進める上で大切にしている価値観を教えてください。",
        "難しい判断を求められたとき、何を基準に決めますか？",
        "情報が不足した状況で意思決定した経験を教えてください。",
        "短期の成果と長期の価値が衝突したら、どう考えますか？",
        "顧客や相手の要望を、そのまま受け入れない方がよいと判断した経験はありますか？",
        "期限が迫る中で品質上の懸念を見つけたら、どう対応しますか？",
        "ルールや倫理と成果が衝突する場面で、どのように行動しますか？",
        "ご自身がやりがいを感じるのは、どのような場面ですか？",
        "苦手な環境でも成果を出すために、どのような工夫をしますか？",
        "周囲と価値観が異なるとき、どのように相互理解を図りますか？",
    ],
    "進路・環境選び": [
        "次の環境を選ぶ上で、最も重視している条件は何ですか？",
        "今回、応募を決めたきっかけを教えてください。",
        "これまでの進路や仕事の選択に、一貫する考え方はありますか？",
        "これまでの環境で得たものと、次の環境で実現したいことを教えてください。",
        "今回の選択で、妥協できることとできないことは何ですか？",
        "他にどのような業界や職種を検討していますか？",
        "複数の企業から内定が出た場合、どのような基準で判断しますか？",
        "当社への志望度と、その理由を率直に教えてください。",
        "入社前に確認しておきたい不安や懸念はありますか？",
        "新しい環境に移ることで、ご自身が変えたいことは何ですか？",
    ],
    "働き方・適応": [
        "複数の業務や課題が重なったとき、どのように優先順位をつけますか？",
        "自分の進捗や課題を周囲に共有する際、工夫していることは何ですか？",
        "状況や方針が途中で変わった経験と、その対応を教えてください。",
        "指示が曖昧な課題に取り組むとき、どのように認識を合わせますか？",
        "遠隔での協働や、会えない相手とのやり取りで気をつけていることは何ですか？",
        "成果を出すために、周囲からどのような支援があるとよいですか？",
        "負荷が高いとき、ご自身の状態をどのように把握・調整しますか？",
        "単調な作業や地道な改善を継続した経験を教えてください。",
        "自分の担当範囲外の問題に気づいたら、どのように動きますか？",
        "新しいチームに入ったとき、最初に意識していることを教えてください。",
    ],
    "入社後の貢献・将来像": [
        "当社に入社したら、まずどのようなことに取り組みたいですか？",
        "入社後の半年間で、どのような状態を目指しますか？",
        "当社の課題に対して、ご自身の経験をどう生かせると考えていますか？",
        "入社後に学び直す必要があることは何だと考えていますか？",
        "希望と異なる業務を任された場合、どのように向き合いますか？",
        "仕事の成果を出すために、最初に誰とどのような関係をつくりたいですか？",
        "3年後、どのような専門性や役割を持っていたいですか？",
        "5〜10年後のキャリアをどのように考えていますか？",
        "当社の成長と、ご自身のキャリアをどうつなげたいですか？",
        "最後に、採用担当者へ伝えておきたいことはありますか？",
    ],
}


def interview_question_list(bp, count):
    """Questions asked by an interviewer; do not invent the applicant's answers."""
    grouped = [(theme, [q.format(role=bp["selected_patterns"]["role"]["name"]) for q in questions])
               for theme, questions in INTERVIEW_QUESTIONS.items()]
    stage = bp["selected_patterns"]["stage"]["id"]
    priority = {"second-interview": "希望職種・専門性", "final-interview": "志望動機・企業理解"}.get(stage)
    if priority:
        grouped.sort(key=lambda entry: entry[0] != priority)
    if count >= 100:
        entries = [(theme, q) for theme, questions in grouped for q in questions]
    else:
        entries = [(theme, questions[i]) for i in range(10) for theme, questions in grouped]
    while len(entries) < count:
        entries.append(("追加の深掘り", f"【想定質問{len(entries) + 1}：経歴や募集要件に応じた深掘りを記入】"))
    return "\n".join(f"{i}. 【{theme}】「{question}」" for i, (theme, question) in enumerate(entries[:count], 1))


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


def generate_full_report(bp: dict, reverse_question_count=None, self_introduction=None,
                         interview_question_count=None) -> str:
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
    interview_count = resolve_interview_question_count(interview_question_count, "full")
    interview_section = (
        f"### ⑤ 企業・面接官から応募者への想定質問（{interview_count}問）\n"
        + interview_question_list(bp, interview_count)
    ) if interview_count else ""
    reverse_section = (
        f"### ⑥ 応募者から企業への逆質問（{count}問：一次情報の事実＋現場仮説＋問い）\n"
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

{interview_section}

{reverse_section}
"""


def generate_cheatsheet(bp: dict, reverse_question_count=None, self_introduction=None,
                        interview_question_count=None) -> str:
    company = bp["target_company"]
    comps = bp["competitors"]
    comp_a = comps[0] if len(comps) > 0 else "競合A社"
    sp = bp["selected_patterns"]
    role = bp["step3_role_analysis"]
    stage = bp["step4_stage_strategy"]
    count = resolve_question_count(reverse_question_count, "cheatsheet")
    interview_count = resolve_interview_question_count(interview_question_count, "cheatsheet")
    interview_section = (
        f"## 付録A. 企業・面接官から応募者への想定質問（{interview_count}問）\n"
        + interview_question_list(bp, interview_count) + "\n\n"
    ) if interview_count else ""
    reverse_section = (
        f"## 付録B. 応募者から企業への逆質問（{count}問）\n" + reverse_question_list(bp, count)
    ) if count else ""
    priorities = []
    if interview_count:
        priorities.append("- 想定質問集から、回答を最優先で準備する質問番号と回答骨子を記入。")
    if count:
        priorities.append("- 逆質問集から、当日企業に確認する質問番号と選定理由を記入。")
    priority_section = "## 3. 当日の重点\n" + "\n".join(priorities) + "\n\n---\n\n" if priorities else ""

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

{priority_section}{interview_section}{reverse_section}
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
    parser.add_argument("--reverse-question-count", default="auto", help="応募者から企業への逆質問の件数。0で省略、未指定は10問")
    parser.add_argument("--interview-question-count", default="auto", help="企業・面接官から応募者への想定質問の件数。0で省略、未指定は100問")
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
        interview_count = parse_question_count(args.interview_question_count)
    except ValueError as exc:
        parser.error(str(exc))
    offer_report = args.mode != "cheatsheet" and (args.mode == "offer-comparison" or stage_key == "offer-comparison")
    if offer_report and question_count != "auto":
        parser.error("--reverse-question-countはフル版・チートシート向けです。内定比較の確認質問とは別に扱います")
    if offer_report and interview_count != "auto":
        parser.error("--interview-question-countはフル版・チートシート向けです")
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
        md = generate_cheatsheet(bp, question_count, self_introduction, interview_count)
    elif args.mode == "offer-comparison" or stage_key == "offer-comparison":
        md = generate_offer_comparison(bp)
    else:
        md = generate_full_report(bp, question_count, self_introduction, interview_count)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")
        print(f"[OK] Saved report to {out_path}")
    else:
        print(md)


if __name__ == "__main__":
    main()
