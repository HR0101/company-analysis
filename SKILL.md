---
name: company-analysis
description: 業界別・希望職種別・選考フェーズ（ES・1次面接・2次面接・最終面接・オファー比較）別・新卒/中途別のパターンから選択して、一次情報（有価証券報告書・決算説明資料・中期経営計画・統合報告書・採用ピッチ資料・口コミ）に基づく徹底的な企業分析と、競合差別化・志望動機・仮説検証型逆質問の作成を行うスキル。ユーザーが企業分析、企業研究、業界・競合比較、IR分析、または特定企業の選考・面接対策を求めたときに使用する。
metadata:
  short-description: 業界・職種・何次面接かを選べる徹底企業分析＆選考対策スキル
---

# 企業分析＆選考対策マスター（Company Analysis）

企業の表面的なWebサイト要約ではなく、**一次情報（IR資料・採用ピッチ資料・統合報告書）と現場口コミの突合**に基づき、ユーザーが選んだ**「業界 × 希望職種 × 選考フェーズ（何次面接か）× 応募区分 × 企業タイプ」の5軸パターン**に完全最適化した企業分析と選考突破アウトプット（競合比較マトリクス・志望動機・深掘り回答・仮説検証型逆質問）を作成する。

---

## 1. 最初に確定すること（5軸パターン選択システム）

ユーザーの依頼から以下の5軸を確認する。**企業名だけが指定され、希望職種や「何次面接か（選考フェーズ）」が未指定の場合は、[references/output-templates.md](references/output-templates.md) の「1. パターン選択メニュー」を簡潔に提示して選んでもらうか、または企業名から業界・企業タイプを自動判定した上で職種と選考フェーズを確認する**（「おまかせ」「まず全体像を知りたい」と言われた場合は即時フル分析へ進む）。

| 軸 | パターンIDと選択肢 | 詳細リファレンス |
| :--- | :--- | :--- |
| **① 業界パターン** | `it-saas-web` (IT・SaaS・Web・AI・SIer)<br>`consulting` (戦略・総合・ITコンサル・シンクタンク)<br>`manufacturing` (メーカー：電機・自動車・半導体・化学・食品・製薬等)<br>`trading` (総合商社・専門商社)<br>`finance` (金融：銀行・証券・保険・カード・アセマネ・FinTech)<br>`media-ad-entertainment` (広告・メディア・エンタメ・ゲーム)<br>`real-estate-infra-logistics` (不動産・デベロッパー・建設・インフラ・物流)<br>`hr-retail-service-healthcare` (人材・小売・EC・医療・教育・サービス) | [references/industry-patterns.md](references/industry-patterns.md) |
| **② 希望職種パターン** | `sales-cs` (法人営業/個人営業/IS/FS/カスタマーサクセス)<br>`planning-marketing-bizdev` (経営企画/事業企画/商品企画/マーケ/BizDev)<br>`pdm-pm-consultant` (PdM/PM/コンサルタント/プリセールス)<br>`software-ai-engineer` (Web/モバイル/AI/データ/SRE/セキュリティ)<br>`rd-manufacturing-eng` (研究開発R&D/機電・化学設計/生産技術/品質保証)<br>`corporate` (経理財務/人事HR/法務/広報IR/情報システム) | [references/role-patterns.md](references/role-patterns.md) |
| **③ 選考フェーズ（何次面接か）** | `casual-intern-ob` (インターン・OB/OG訪問・カジュアル面談)<br>`es-resume` (書類選考・ES・職務経歴書作成)<br>`first-interview` (**1次面接**：人事・若手〜中堅現場社員向け)<br>`second-interview` (**2次・中盤面接**：現場課長・部長・マネージャー向け)<br>`final-interview` (**最終・役員面接**：社長・取締役・事業本部長向け)<br>`offer-comparison` (内定後・オファー面談・複数社内定比較) | [references/interview-stage-patterns.md](references/interview-stage-patterns.md) |
| **④ 応募区分** | `new-grad` (新卒就活) / `mid-career` (中途転職) / `second-new-grad` (第二新卒) | [references/interview-stage-patterns.md](references/interview-stage-patterns.md) |
| **⑤ 企業タイプ** | `listed-enterprise` (日系大手・上場) / `mega-venture` (メガベンチャー) / `startup-unlisted` (未上場スタートアップ) / `foreign-affiliated` (外資系) | [references/secrets-and-methodology.md](references/secrets-and-methodology.md) |

### ブループリントの即時生成（スクリプト活用）
パターンが決まったら（または一覧を確認したいときは）、同梱スクリプトを実行して対象パターン専用の分析・選考攻略ブループリントを生成できる。

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

分析を開始する前に必ず [references/secrets-and-methodology.md](references/secrets-and-methodology.md) の原則を押さえ、該当する業界・職種・選考フェーズのリファレンスだけを読み込む。

### Step 1：一次情報からのファクト収集（Web検索・提供資料の精査）
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
財務数値や従業員データ・口コミ傾向が得られた場合は、`scripts/financial_analyzer.py` を実行して定量指標・キャッシュフロー8パターン診断・OpenWork×統合報告書のギャップ診断を行う。

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
  - レーダーチャート形状から「真のホワイト優良型」「若手ハードワーク・早期成長特化型」「ゆるブラック（ぬるま湯・成長停滞）注意型」「公式発表との乖離注意型」を判定し、入社後のミスマッチや配属リスクを警告する。

### Step 3：「調べて終わり」を「選考突破」に変える3大変換
収集した事実をそのまま並べるのではなく、必ず以下の3つに変換する（詳細は [references/secrets-and-methodology.md](references/secrets-and-methodology.md) のセクション5参照）：
1. **競合比較マトリクス → 「なぜ同業他社ではなく御社か（Why This Company）」**:
   - 同業ライバル2〜3社を並べ、事業ポートフォリオ・顧客層・収益構造・中計の投資先・カルチャーの違いを比較表にする。
2. **企業の課題仮説 × 応募者の強み → 「再現性（Why Me）」**:
   - 有報の「対処すべき課題」や中計の「注力テーマ」から、希望職種（`role`）の現場が直面しているボトルネックを仮説立て、応募者の経験がどう活きるかを接続する。
3. **一次情報の事実 ＋ 現場仮説 → 「仮説検証型・逆質問（Reverse Questions）」**:
   - `【IR・公式情報の事実】＋【自分なりの現場仮説】＋【面接官の役職に応じた問い】` の構文で、選考フェーズ（1次＝現場若手・人事、2次＝現場課長・部長、最終＝社長・役員）にぴったりの逆質問を設計する。

---

## 3. 出力フォーマットの選択と生成

ユーザーの状況と選考フェーズに応じて、[references/output-templates.md](references/output-templates.md) または `scripts/report_generator.py` を使って最適な形式で出力する。

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
   - 売上高、利益、平均年収、有給取得率などの定量データは、確認できた事実（年度・出典を明記）のみを記載する。未確認・非公開の項目は推測で数字を埋めず、「非公開（確認ポイント：〇〇）」と明記する。
2. **「何次面接か」に応じた視座の厳密な使い分け**:
   - **1次面接**では「端的な結論ファースト（45〜60秒）・基礎理解・素直さと協働性」を重視し、頭でっかちな経営批判を避ける。
   - **2次面接**では「競合他社との明確な比較・志望職種での実務再現性・現場マネージャー目線の課題仮説」を重視する。
   - **最終面接**では「第一志望の覚悟・企業理念（VMV）と原体験の一致・5〜10年後の長期ビジョン」を重視する。
3. **ポジティブ一辺倒の「ファンレター」化を防ぐ**:
   - 企業の強みだけでなく、有報のリスク項目や業界の構造的課題、口コミから見える組織のリアルな注意点（配属ガチャ、ハードワーク度合い、ゆるブラックリスク等）も客観的かつ建設的に提示する。
