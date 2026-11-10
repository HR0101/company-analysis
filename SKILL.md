---
name: company-analysis
description: 業界別・希望職種別・選考フェーズ（ES・1次面接・2次面接・最終面接・オファー比較）別・新卒/中途別のパターンから選択して、一次情報（有価証券報告書・決算説明資料・中期経営計画・統合報告書・採用ピッチ資料）と参考情報としての口コミに基づく徹底的な企業分析と、競合差別化・約1分の自己紹介・志望動機・仮説検証型逆質問・想定質問100問の作成を行うスキル。ユーザーが企業分析、企業研究、業界・競合比較、IR分析、または特定企業の選考・面接対策を求めたときに使用する。
metadata:
  short-description: 業界・職種・何次面接かを選べる徹底企業分析＆選考対策スキル
---

# 企業分析＆選考対策マスター（Company Analysis）

一次情報（IR資料・採用ピッチ資料・統合報告書）に基づき、依頼の目的に合わせた企業分析を行う。口コミは未検証の参考情報として区別する。選考対策が求められた場合は、5軸パターンを使い、競合比較・約1分の自己紹介・志望動機・深掘り回答・仮説検証型逆質問（標準10問）・面接官からの想定質問（標準100問）へ展開する。

## 参照ファイルとスクリプトの場所（Codex / Claude 両対応）

- **Codex（CLI / デスクトップアプリ）およびスキル直配置（`~/.codex/skills/company-analysis/`、`~/.agents/skills/company-analysis/`、`~/.claude/skills/company-analysis/`）の場合**:
  - この `SKILL.md` と同じディレクトリの `references/` と `scripts/` を使う。
- **Claude Code のプラグインとして導入した場合**:
  - `${CLAUDE_PLUGIN_ROOT}/skills/company-analysis/references/`
  - `${CLAUDE_PLUGIN_ROOT}/skills/company-analysis/scripts/`

以降のパス表記はスキルディレクトリからの相対で書く。

---

## 1. 依頼の目的と必要な条件を確認する

- **入力UIで開始**: 「入力UIで始めたい」「項目を選んで分析したい」、または対象企業・目的が未指定のスキル起動（`$company-analysis`、`/company-analysis`、`/company-analysis:company-analysis` のみ等）では、[references/input-ui.md](references/input-ui.md) に従い、利用可能な質問ツール（Codex の `request_user_input_async` / `request_user_input`、または Claude Code の `AskUserQuestion`）を実際に呼び出す。`scripts/input_ui.py` が生成する引数で企業名・目的・必要な軸を入力/選択してもらう。JSONやMarkdownのメニューを表示しただけで「UIを表示した」としない。質問UIが利用できない場合は短いテキスト質問に切り替える。
- **企業研究・IR分析・業界/競合比較**: 業界・企業タイプと依頼された論点を中心に分析する。企業名だけの依頼も、まず全体像の企業研究として進める。希望職種・選考フェーズ・応募区分の確認や、志望動機・逆質問の作成は不要。以下の5軸のうち必要な軸だけを使う。
- **応募・選考対策**: ユーザーが伝えた情報から以下の5軸を設定する。不足が成果物に影響する場合のみ、[references/input-ui.md](references/input-ui.md) の質問UIで必要な条件を確認する。回答済みの項目は聞かず、業界・企業タイプは推定可能なら補う。「おまかせ」の場合は仮定を明示して進める。本人の経歴・実績・志望度は創作しない。


| 軸 | パターンIDと選択肢 | 詳細リファレンス |
| :--- | :--- | :--- |
| **① 業界パターン** | `it-saas-web` (IT・SaaS・Web・AI・SIer)<br>`consulting` (戦略・総合・ITコンサル・シンクタンク)<br>`manufacturing` (メーカー：電機・自動車・半導体・化学・食品・製薬等)<br>`trading` (総合商社・専門商社)<br>`finance` (金融：銀行・証券・保険・カード・アセマネ・FinTech)<br>`media-ad-entertainment` (広告・メディア・エンタメ・ゲーム)<br>`real-estate-infra-logistics` (不動産・デベロッパー・建設・インフラ・物流)<br>`hr-retail-service-healthcare` (人材・小売・EC・医療・教育・サービス) | [references/industry-patterns.md](references/industry-patterns.md) |
| **② 希望職種パターン** | `sales-cs` (法人営業/個人営業/IS/FS/カスタマーサクセス)<br>`planning-marketing-bizdev` (経営企画/事業企画/商品企画/マーケ/BizDev)<br>`pdm-pm-consultant` (PdM/PM/コンサルタント/プリセールス)<br>`software-ai-engineer` (Web/モバイル/AI/データ/SRE/セキュリティ)<br>`rd-manufacturing-eng` (研究開発R&D/機電・化学設計/生産技術/品質保証)<br>`corporate` (経理財務/人事HR/法務/広報IR/情報システム) | [references/role-patterns.md](references/role-patterns.md) |
| **③ 選考フェーズ（何次面接か）** | `casual-intern-ob` (インターン・OB/OG訪問・カジュアル面談)<br>`es-resume` (書類選考・ES・職務経歴書作成)<br>`first-interview` (**1次面接**：人事・若手〜中堅現場社員向け)<br>`second-interview` (**2次・中盤面接**：現場課長・部長・マネージャー向け)<br>`final-interview` (**最終・役員面接**：社長・取締役・事業本部長向け)<br>`offer-comparison` (内定後・オファー面談・複数社内定比較) | [references/interview-stage-patterns.md](references/interview-stage-patterns.md) |
| **④ 応募区分** | `new-grad` (新卒就活) / `mid-career` (中途転職) / `second-new-grad` (第二新卒) | [references/interview-stage-patterns.md](references/interview-stage-patterns.md) |
| **⑤ 企業タイプ** | `listed-enterprise` (日系大手・上場) / `mega-venture` (メガベンチャー) / `startup-unlisted` (未上場スタートアップ) / `foreign-affiliated` (外資系) | [references/secrets-and-methodology.md](references/secrets-and-methodology.md) |

### ブループリントの即時生成（スクリプト活用）
選考対策のパターンが決まったら（または一覧を確認したいときは）、同梱スクリプトでブループリントを生成できる。企業研究のみの依頼では、不要な選考軸を埋めるためにこのスクリプトを実行する必要はない。

以下のコマンドの `scripts/` は、この `SKILL.md` があるディレクトリ（Claude プラグイン導入時は `${CLAUDE_PLUGIN_ROOT}/skills/company-analysis/`）を基準に解決する。未知・曖昧な指定はエラーになるため、有効なIDを使って再指定する。

```bash
# 全パターンの一覧表示
python3 scripts/pattern_selector.py --list

# 指定パターンの攻略ブループリント出力（日本語キーワードや略称も自動解決）
python3 scripts/pattern_selector.py \
  --company "対象企業名" \
  --industry "IT" \
  --role "エンジニア" \
  --stage "2次面接" \
  --candidate "中途" \
  --archetype "メガベンチャー" \
  --competitors "競合A社,競合B社"
```

---

## 2. 企業分析のコア手順（秘訣の適用）

分析を開始する前に必ず [references/secrets-and-methodology.md](references/secrets-and-methodology.md) の原則を押さえ、依頼に必要な業界・職種・選考フェーズのリファレンスだけを読み込む。企業研究では職種・選考フェーズのリファレンスは不要。

### Step 1：一次情報からのファクト収集（Web検索・提供PDF/資料の精査）
- **添付PDF・ローカル資料の読み取り**:
  - ユーザーが有価証券報告書・決算説明資料・中期経営計画・統合報告書・求人票・履歴書/職務経歴書などのPDFやファイルを指定・添付した場合は、ファイル読み取りツール（Claude の `Read` ツールでは10ページ超のPDFは `pages` 指定で最大20ページずつ）で直接精査する。
- **上場企業（`listed-enterprise` / `mega-venture`）**:
  - **有価証券報告書**（事業の内容、セグメント別売上・利益、対処すべき課題、**事業等のリスク**、従業員の平均年齢・勤続年数・平均年間給与）
  - **決算説明資料**（直近通期・四半期の業績ハイライト、KPI推移、前年比増減要因）
  - **中期経営計画**（3〜5年後の定量目標、成長投資領域、事業ポートフォリオ改革）
  - **統合報告書**（CEOメッセージ、価値創造プロセス、人的資本データ）
- **未上場スタートアップ（`startup-unlisted`）**:
  - **採用ピッチ資料（Company Deck / Culture Deck）**、**PR TIMESの資金調達リリース**（ラウンド・累計調達額・引受先VC/事業会社）、**官報決算公告**、**創業者インタビュー・Wantedly**。
- **外資系企業（`foreign-affiliated`）**:
  - **グローバル本社 Annual Report / Form 10-K** と、**日本法人（Japanオフィス）のミッション範囲**（営業・マーケ拠点か、日本独自の企画・R&D・開発権限があるか）、**Job Description（JD）の要件分解**。

### Step 2：財務・キャッシュフロー・人的資本ギャップ診断
財務数値や従業員データ・口コミ指標が得られた場合は、`scripts/financial_analyzer.py` で定量指標・CFの符号分類と金額の関係・入力済みの口コミ指標を整理できる。年度・通貨単位・単体/連結の対象範囲を揃えて入力し、出典はレポートに別途付記する。

```bash
python3 scripts/financial_analyzer.py \
  --company "対象企業名" \
  --revenue 1500 --prev-revenue 1350 --gross-profit 600 --operating-profit 180 --net-profit 120 \
  --total-assets 2000 --equity 1000 --employees 3500 \
  --operating-cf 220 --investing-cf -140 --financing-cf -50 \
  --avg-age 36.2 --avg-tenure 11.4 --avg-salary 850 \
  --ow-overall 3.7 --ow-growth20s 3.5 --ow-compliance 4.1
```

- **公式発表（統合報告書・採用HP）と現場体感（OpenWork等）の突合**:
  - 口コミの投稿時期・件数・職種・部署と公式情報の対象範囲を確認し、違いを検証すべき仮説として整理する。未入力指標や口コミだけから待遇・労働時間・法令順守の実態、企業全体の良否を断定しない。スクリプトは公式資料との突合を自動実行しない。
- **CFの解釈**: 符号8分類は資金の流入/流出を表す。投資・調達の目的や健全性は、金額、期首/期末現預金、返済予定、内訳、複数年の推移を確認してから評価する。ゼロは正負どちらにも分類しない。

### Step 3：「調べて終わり」を「選考突破」に変える3大変換
**応募・選考対策を依頼された場合のみ**、収集した事実を以下の3つに変換する（詳細は [references/secrets-and-methodology.md](references/secrets-and-methodology.md) のセクション5参照）：
1. **競合比較マトリクス → 「なぜ同業他社ではなく御社か（Why This Company）」**:
   - 同業ライバル2〜3社を並べ、事業ポートフォリオ・顧客層・収益構造・中計の投資先・カルチャーの違いを比較表にする。
2. **企業の課題仮説 × 応募者の強み → 「再現性（Why Me）」**:
   - 有報の「対処すべき課題」や中計の「注力テーマ」から、希望職種（`role`）の現場が直面しているボトルネックを仮説立て、応募者の経験がどう活きるかを接続する。
3. **一次情報の事実 ＋ 現場仮説 → 「仮説検証型・逆質問（Reverse Questions）」**:
   - `【IR・公式情報の事実】＋【自分なりの現場仮説】＋【面接官の役職に応じた問い】` の構文で、選考フェーズ（1次＝現場若手・人事、2次＝現場課長・部長、最終＝社長・役員）にぴったりの逆質問を設計する。

---

## 3. 出力フォーマットの選択と生成

企業研究・IR分析・競合比較には、[references/output-templates.md](references/output-templates.md) の「0. 企業研究・IR分析向け」を使い、依頼された論点に絞る。応募・選考対策には同ファイルの選考用テンプレートまたは `scripts/report_generator.py` を使う。スクリプトは空欄付きのワークシートを生成するため、確認済み資料で内容を補ってから納品する。テンプレートそのものを求められた場合は空欄のままでよい。

質問は次の2種類を明確に分け、入力UI・見出し・件数設定を混同しない。フル版・直前版とも共通の標準件数を使う。

- **逆質問（応募者 → 企業・面接官）**: 標準10問。`reverse_question_count` と `--reverse-question-count N` で指定する。一次情報に基づく事実＋現場仮説＋相手に確認する問いで構成し、裏付けのない前提を置かない。
- **想定質問（企業・面接官 → 応募者）**: 標準100問。`interview_question_count` と `--interview-question-count N` で指定する。自己紹介、志望動機・企業理解、職種・専門性、成果・課題解決、協働、失敗・学習、価値観、進路選択、働き方、入社後の貢献など10テーマ程度で構成する。希望職種・応募区分・選考フェーズ・本人の経歴に合わせ、面接官が応募者に尋ねる文にする。優先する質問には面接官の確認意図と回答骨子を添え、本人の未確認の経歴や実績を回答として創作しない。

いずれも入力UIまたはユーザーの指定件数を優先し、0問ならその種類だけを省略する。納品時に種類別の件数・通し番号・意味の重複を確認する。直前版では短い本文と2種類の質問集を分け、準備を優先する想定質問と、当日企業に尋ねる逆質問の番号を別々に示す。企業研究と内定比較ではこれらの件数を適用しない。

選考対策のフル版・直前版には、[references/self-introduction.md](references/self-introduction.md) に従い、利用可能な会話履歴・提供済みの経歴資料から**約1分の自己紹介**を自動作成する。志望動機とは別に、現在の所属→代表的な経験・成果→強み→結びの読み上げ原稿を250〜350字を目安にまとめる。経歴が揃っていれば再入力を求めない。不足する場合のみ必要事項を質問UIで1問にまとめて確認する。参照できない過去チャットや、本人の実績として確認できない情報を使わない。スクリプトで出力するときは完成原稿を一時ファイルへ保存し、`--self-introduction-file` に渡す。

```bash
# フル企業分析＆選考突破マスターシートの生成（--mode full）
python3 scripts/report_generator.py \
  --company "対象企業名" --industry "商社" --role "企画" --stage "2次面接" \
  --candidate "新卒" --archetype "日系大手" --competitors "競合A社,競合B社" --mode full

# 面接直前5分チートシートの生成（--mode cheatsheet）
python3 scripts/report_generator.py \
  --company "対象企業名" --industry "IT" --role "営業" --stage "最終面接" --mode cheatsheet

# 内定後・オファー比較スコアカードの生成（--mode offer-comparison）
python3 scripts/report_generator.py \
  --company "第一志望社" --competitors "併願内定A社,併願内定B社" --mode offer-comparison
```

---

## 4. 厳守すべき品質ガードレール

1. **数値と事実の捏造禁止（No Hallucination）**:
   - 売上高、利益、平均年収、有給取得率などの定量データは、確認できた事実（年度・出典を明記）のみを記載する。不足項目を推測で埋めない。「未確認（未調査・根拠未確認）」「取得不可（資料へのアクセス失敗・閲覧制限）」「非公開（非開示であることを確認）」を区別し、確認方法・参照資料を添える。検索で見つからなかっただけで非公開としない。口コミに共通する記述も、一次情報等で裏付けるまでは「口コミの傾向・仮説」として扱う。
2. **選考対策の場合の視座の使い分け**:
   - 面接官の役職・担当や募集要項が分かっている場合は、その情報を面接回数からの推定より優先する。以下は一般的な目安とする。
   - **1次面接**では「端的な結論ファースト（45〜60秒）・基礎理解・素直さと協働性」を重視し、頭でっかちな経営批判を避ける。
   - **2次面接**では「競合他社との明確な比較・志望職種での実務再現性・現場マネージャー目線の課題仮説」を重視する。
   - **最終面接**では「第一志望の覚悟・企業理念（VMV）と原体験の一致・5〜10年後の長期ビジョン」を重視する。
3. **ポジティブ一辺倒の「ファンレター」化を防ぐ**:
   - 企業の強みだけでなく、有報のリスク項目や業界の構造的課題、口コミから得た要確認の論点も、確認済みの事実と仮説を分けて建設的に提示する。
