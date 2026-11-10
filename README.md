# company-analysis-codex（企業分析＆選考対策マスター）

[![Validate Plugin & Skill](https://github.com/HR0101/company-analysis-codex/actions/workflows/validate.yml/badge.svg)](https://github.com/HR0101/company-analysis-codex/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-0284C7.svg)](LICENSE)

**`company-analysis`** は、ネットで体系化された企業分析・業界研究・選考対策の秘訣（有価証券報告書・決算説明資料・中期経営計画・統合報告書・採用ピッチ資料の一次情報5大ソース解読、およびOpenWork等の現場口コミとの突合メソッド）をベースに、**「①業界 × ②希望職種 × ③何次面接か（選考フェーズ） × ④新卒/中途 × ⑤企業タイプ」の5軸パターン**から選んで徹底的な企業分析と選考対策を行う **Codex スキル＆デスクトップアプリ対応プラグイン**です。

Codex CLI はもちろん、**ChatGPT / Codex デスクトップアプリ（macOS App）** のスキル＆プラグイン（UIカード・アイコン・ワンクリック開始プロンプト付き）として誰でもすぐに導入・利用できます。

---

## 特長（なぜこのスキルで内定率が上がるのか）

1. **「誰でも言える企業理念への共感」を脱却する一次情報5大ソース解読メソッド**
   - **有価証券報告書（EDINET）**：セグメント別利益率、【事業等のリスク】、【設備投資・研究開発】、人的資本指標（平均年間給与・平均勤続年数・女性管理職比率）から「本当の稼ぎ頭」と「経営課題」を特定
   - **決算説明資料・中期経営計画**：経営陣が投資家にコミットしているKPI（ARR・NRR・ROE・ROIC等）と今後3〜5年の最重点投資領域を抽出
   - **統合報告書 × OpenWork（口コミ）のギャップ突合**：会社が掲げる理想と現場のリアル（20代成長環境・風通し・法令順守意識のスコア差）を掛け合わせ、入力済みの口コミ評価と公式開示の違いを検証するための論点を整理（口コミだけで企業全体の良否は判定しません）
2. **「5軸パターン選択」であなた専用の分析・対策シートに自動最適化**
   - **8大業界（25サブセクター） × 6大職種（20専門ロール） × 6選考フェーズ（何次面接か） × 候補者属性（新卒/中途/第二新卒） × 企業タイプ（日系大手/メガベンチャー/未上場スタートアップ/外資系）** の組み合わせから最適な分析項目・評価基準・逆質問を自動設計
3. **「何次面接か」に応じた面接官の役職プロファイリングと仮説検証型逆質問**
   - 1次面接（現場社員・主任）、2次面接（課長・部長・PM）、最終面接（役員・社長・人事統括）ごとに「合格の決め手」と「NG発言」を明確化
   - ググればわかる質問を排除し、`【一次情報の事実】＋【自分の仮説】＋【面接官の視座への問い】` から成る**仮説検証型逆質問**を生成
4. **Python標準ライブラリ完結の入力UI補助・分析スクリプトを同梱**
   - 外部パッケージ不要（Python 3.9+ 標準ライブラリのみ）で動作する `input_ui.py`・`pattern_selector.py`・`financial_analyzer.py`・`report_generator.py` を内蔵し、キャッシュフロー8パターン診断やSaaS Rule of 40算出、Markdownレポート出力を自動化

---

## インストール方法（誰でも1分で導入可能）

### 方法A：ワンライナーで一括インストール（推奨・CLI＆デスクトップアプリ両対応）

以下の1行をターミナルで実行すると、`~/.codex/skills/company-analysis`、`~/.agents/skills/company-analysis`、およびデスクトップアプリ用プラグイン（`~/.codex/plugins/company-analysis` と `~/.agents/plugins/marketplace.json`）へ一括で配置し、CLIが利用可能なら有効化を試みます。既存のマーケットプレイス設定が不正な場合は変更前に停止し、正常な既存設定の更新時には同じディレクトリへ一意な `.bak` ファイルを保存します。

```bash
curl -fsSL https://raw.githubusercontent.com/HR0101/company-analysis-codex/main/install.sh | bash
```

---

### 方法B：ChatGPT / Codex デスクトップアプリのプラグインマーケットプレイスから追加

Codex CLI（または ChatGPT.app 同梱の `codex` バイナリ）を使って、GitHub リポジトリをプラグインマーケットプレイスとして直接登録・インストールできます。

```bash
# 1. GitHub リポジトリをマーケットプレイスとして登録
codex plugin marketplace add HR0101/company-analysis-codex

# 2. プラグインをインストール＆有効化
codex plugin add company-analysis@company-analysis-codex
```

> **macOS で `codex` コマンドにパスが通っていない場合**：
> ChatGPT デスクトップアプリ同梱の CLI を直接呼び出せます：
> ```bash
> /Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex plugin marketplace add HR0101/company-analysis-codex
> /Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex plugin add company-analysis@company-analysis-codex
> ```

---

### 方法C：Codex 内の `$skill-installer` で導入する

Codex（デスクトップアプリまたは CLI）のチャット欄で、以下のように話しかけるだけで導入できます：

```text
$skill-installer GitHub の HR0101/company-analysis-codex から skills/company-analysis をインストールして
```

またはコマンドで直接実行する場合：

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo HR0101/company-analysis-codex \
  --path skills/company-analysis
```

---

### 方法D：`git clone` 1行でスキルディレクトリへ配置する

リポジトリ直下にも `SKILL.md` を配置しているため、そのままスキルフォルダへ `git clone` するだけでも動作します。

```bash
# ~/.agents/skills に配置する場合
git clone https://github.com/HR0101/company-analysis-codex.git ~/.agents/skills/company-analysis

# ~/.codex/skills に配置する場合
git clone https://github.com/HR0101/company-analysis-codex.git ~/.codex/skills/company-analysis
```

> インストール後、ChatGPT / Codex デスクトップアプリを起動中の方は、**アプリを再起動するか新しいスレッド（New Thread）を開く**と `$company-analysis` スキルとプラグインUIが読み込まれます。

---

## デスクトップアプリ＆CLIでの使い方

企業研究・IR分析・業績比較だけの依頼では、職種や面接フェーズを指定する必要はありません。企業名だけでも全体像の分析から始められます。志望動機・逆質問は選考対策を依頼した場合に作成します。

チャット欄で `$company-analysis` をメンションするか、そのまま自然言語で「〇〇の企業分析をして」「〇〇の2次面接対策をして」と話しかけてください。

### 入力UIで始める

スキルカードの開始プロンプト、または次の一言で始められます。条件をまとめた長いプロンプトを書く必要はありません。

```text
$company-analysis 入力UIで始めて
```

対応環境では、企業名・分析目的を入力した後、業界・職種・選考フェーズ・応募区分・企業タイプ・出力形式を質問UIで選びます。一度に最大3問ずつ表示し、回答済みの項目は聞き直しません。候補数に制限があるUIでは、グループから個別項目へ段階的に選べます。「おまかせ・未定」も選択できます。

選考対策では、出力形式の後に次の2種類の件数を別々に指定できます。標準件数はフル版・直前版で共通です。

| 種類 | 誰から誰への質問か | 標準件数 | UIの候補 |
| :--- | :--- | :--- | :--- |
| **逆質問** | 応募者から企業・面接官へ | **10問** | 標準・3問・5問・10問・不要 |
| **想定質問** | 企業・面接官から応募者へ | **100問** | 標準・10問・50問・100問・不要 |

「7問」などの自由入力も可能です。想定質問は経歴、志望動機、職種、経験・成果、協働、失敗、価値観などのテーマ別に整理します。直前版では優先して回答を準備する想定質問と、当日企業に尋ねる逆質問の番号を別々に本文へ示します。企業研究と内定比較では、この2種類の件数は尋ねません。

選考対策には、利用可能な会話履歴や提供済みの経歴資料から作る**約1分の自己紹介**も含めます。現在の所属・代表的な経験や成果・強みを250〜350字を目安にまとめます。経歴が十分なら再入力を求めず、不足する場合だけ質問します。参照できない過去チャットを読み込んだり、未確認の経歴を補ったりはしません。

企業研究では職種・選考フェーズ・応募区分を尋ねず、内定比較では比較企業の入力へ進みます。企業名や条件を最初から指定した通常の依頼は、そのまま分析できます。

表示はホストの質問ツールに依存します。利用できない環境では短いテキスト質問へ切り替えます。専用フォームや別ウィンドウは追加しません。詳細は [入力UIの動作](references/input-ui.md) を参照してください。

### プロンプト例（コピペして使えます）

#### 1. パターン一覧から選んで対話形式で始めたいとき
```text
$company-analysis パターン一覧を見せて。業界・職種・何次面接かを選んで企業分析を始めたい
```

#### 2. 企業名・業界・希望職種・何次面接かを指定してフル分析シートを作りたいとき
```text
$company-analysis
対象企業：東京エレクトロン（競合：アドバンテスト、ディスコ）
業界：メーカー（半導体製造装置）
希望職種：研究開発・フィールドエンジニア
選考フェーズ：2次面接（現場部長クラス）
応募枠：新卒（理系院生）
有価証券報告書や中期経営計画の観点を踏まえて、競合比較・強みと課題・志望動機・部長面接で刺さる仮説検証型逆質問まで完全版シートを作成して。
```

#### 3. IT・SaaS企業の中途採用（PM・事業企画）で1次面接対策をしたいとき
```text
$company-analysis
マネーフォワードの企業分析をして。
業界：IT・SaaS、希望職種：PdM（プロダクトマネージャー）、選考フェーズ：1次面接、応募枠：中途採用。
競合のfreeeやラクスとのARR・NRR・ターゲット顧客の違いを比較し、1次面接で評価される再現性アピールと逆質問を作って。
```

#### 4. 面接直前5分で確認できるチートシートを作りたいとき
```text
$company-analysis 三菱商事の最終面接（役員面接）直前5分チートシートを作って。三井物産・伊藤忠商事との非資源・ROIC戦略の違いと、最終面接で絶対に外せない覚悟の伝え方・逆質問3選に絞ってまとめて。
```

#### 5. 複数社の内定比較・オファー面談の意思決定をしたいとき
```text
$company-analysis 内定比較モードで、NTTデータと野村総合研究所（NRI）とアクセンチュアの3社を「SE・ITコンサル職／20代成長環境／年収水準／5年後の市場価値」の観点で比較し、オファー面談で確認すべき質問リストを作って。
```

---

## 選べる5軸パターンカタログ

| 軸 | 選択肢（パターンID / 日本語指定どちらも対応） |
| :--- | :--- |
| **① 業界 (`industry`)** | `it-saas-web`（IT・SaaS・Web・AI） / `manufacturing`（メーカー：半導体・自動車・電機・化学・食品） / `trading`（商社：総合商社・専門商社） / `finance`（金融：メガバンク・証券・保険・アセマネ・PE） / `consulting`（コンサル：戦略・総合・IT・FAS） / `real-estate-infra-logistics`（インフラ・不動産・デベロッパー・物流） / `media-ad-entertainment`（広告・メディア・エンタメ・ゲーム） / `hr-retail-service-healthcare`（小売・人材・医療ヘルステック・サービス） |
| **② 希望職種 (`role`)** | `sales-cs`（営業・法人営業・海外営業・アライアンス） / `planning-marketing-bizdev`（商品企画・マーケ・経営企画・新規事業BizDev） / `pdm-pm-consultant`（PdM・PM・コンサルタント・プリセールス） / `software-ai-engineer`（SWE・AIエンジニア・データサイエンティスト） / `rd-manufacturing-eng`（研究開発R&D・生産技術・品質管理・機電系） / `corporate`（コーポレート：経理財務・法務・人事・広報IR） |
| **③ 何次面接か (`stage`)** | `casual-intern-ob`（カジュアル面談・OB/OG訪問・座談会） / `es-resume`（ES・職務経歴書・書類選考） / `first-interview`（1次面接：現場社員・人事） / `second-interview`（2次面接：課長・部長・PM） / `final-interview`（最終面接：社長・役員・人事統括） / `offer-comparison`（内定後オファー面談・複数社内定比較） |
| **④ 候補者属性 (`candidate`)** | `new-grad`（新卒：学部・修士・博士） / `mid-career`（中途・キャリア採用） / `second-new-grad`（第二新卒・既卒・ポテンシャル転職） |
| **⑤ 企業タイプ (`archetype`)** | `listed-enterprise`（日系大手・上場プライム企業） / `mega-venture`（メガベンチャー・上場グロース企業） / `startup-unlisted`（未上場スタートアップ：シード〜レイター） / `foreign-affiliated`（外資系企業：テック・コンサル・金融・消費財） |

---

## 同梱CLIスクリプトの単体実行方法

スキル内の `scripts/` には、Python標準ライブラリのみで動作する4つのCLIツールが同梱されています。ターミナルから直接呼び出すことも可能です。

未指定の軸にはCLIの既定値を使います。明示した指定が未知・曖昧な場合はエラーになるため、`--list` でIDを確認してください。補足付きの日本語も扱えます（例：`2次面接（現場部長クラス）`、`第二新卒（社会人2年目）`）。

### 0. `input_ui.py`（質問UIの引数生成）

次のコマンドはホストの質問ツールに渡すJSONを生成します。ターミナルに入力画面を表示するコマンドではありません。スキルが利用可能なツールを呼び出して表示します。

```bash
python3 scripts/input_ui.py --ui async
```

`--ui standard` は選択肢数が制限された質問ツール、`--ui text` はテキスト質問用です。`--state` に既知の条件をJSONで渡すと残りの項目だけを返します。

### 1. `pattern_selector.py`（5軸パターン一覧＆分析ブループリント生成）

```bash
# 全パターン一覧の表示
python3 scripts/pattern_selector.py --list

# 5軸を指定して分析設計図（Blueprint）を出力
python3 scripts/pattern_selector.py \
  --company "ソニーグループ" \
  --industry "メーカー" \
  --role "商品企画" \
  --stage "2次面接" \
  --candidate "新卒" \
  --archetype "日系大手" \
  --competitors "パナソニック,日立製作所"
```

### 2. `financial_analyzer.py`（財務KPI計算・CF 8パターン診断・人的資本×OpenWork突合診断）

```bash
python3 scripts/financial_analyzer.py \
  --company "サンプルSaaS株式会社" \
  --revenue 180 --prev-revenue 135 \
  --gross-profit 144 --operating-profit 27 --net-profit 18 \
  --total-assets 220 --equity 130 --employees 350 \
  --operating-cf 35 --investing-cf -18 --financing-cf -5 \
  --avg-age 32.4 --avg-tenure 4.2 --avg-salary 820 \
  --ow-overall 4.15 --ow-growth20s 4.4 \
  --ow-compliance 3.9 --ow-evaluation 3.8
```

CF診断は符号分類と金額の関係を整理するもので、資金繰りの健全性の断定には現預金・返済予定・複数年の資料が別途必要です。口コミ診断も入力済みの評価だけを使い、不足する指標は判定不能とします。

### 3. `report_generator.py`（選考対策用ワークシートの生成）

出力は空欄付きのひな形です。完成レポートには確認済みの資料で内容を補い、数値の年度・出典を記載してください。

`--reverse-question-count 10` は応募者から企業への逆質問を10問、`--interview-question-count 100` は企業側から応募者への想定質問を100問に設定します。未指定時もそれぞれ10問・100問です。0にした種類だけを省略できます。入力UIの2種類の件数は対応する引数へ別々に渡します。内定比較の確認質問とは別の設定です。

自己紹介はスキルが利用可能な会話履歴から作成します。CLI単体では会話履歴を取得しないため、完成原稿をUTF-8ファイルに保存し、`--self-introduction-file 原稿ファイル.txt` で渡してください。未指定時は記入欄になります。

```bash
# 完全版マスターシート (--mode full)、直前5分チートシート (--mode cheatsheet)、内定比較シート (--mode offer-comparison) に対応
python3 scripts/report_generator.py \
  --company "サンプル株式会社" \
  --industry "IT" \
  --role "エンジニア" \
  --stage "最終面接" \
  --candidate "中途" \
  --archetype "メガベンチャー" \
  --competitors "競合A社,競合B社" \
  --mode full --reverse-question-count 10 --interview-question-count 100 \
  --output company_analysis_report.md
```

---

## リポジトリ構成

```text
company-analysis-codex/
├── SKILL.md                               # ルート配置スキル定義（git clone 直配置用）
├── agents/openai.yaml                     # OpenAI / Codex スキルUIメタデータ
├── references/                            # 企業分析メソッド＆5軸パターン辞書
│   ├── secrets-and-methodology.md         # 一次情報5大ソース解読・口コミ突合・逆質問の黄金公式
│   ├── industry-patterns.md               # 8大業界・25サブセクター別パターン辞書
│   ├── role-patterns.md                   # 6大職種・20専門ロール別パターン辞書
│   ├── interview-stage-patterns.md        # 6選考フェーズ（何次面接か）×新卒/中途×企業タイプ別対策
│   ├── output-templates.md                # 出力フォーマット＆トークスクリプトテンプレート
│   ├── input-ui.md                        # 質問ツールの呼び出し・入力フロー
│   └── self-introduction.md               # 会話履歴に基づく約1分の自己紹介
├── scripts/                               # Python標準ライブラリ完結の入力UI補助・分析スクリプト
│   ├── input_ui.py                        # 質問UIの引数生成・回答済み条件の引き継ぎ
│   ├── pattern_selector.py                # 5軸パターン選択＆分析ブループリント生成CLI
│   ├── financial_analyzer.py              # 財務指標・CF 8パターン・OpenWork突合診断CLI
│   └── report_generator.py                # 3モード対応Markdownレポート生成CLI
├── assets/                                # デスクトップアプリ用SVG/PNGアイコン＆ロゴ
├── skills/company-analysis/               # $skill-installer (--path skills/company-analysis) 用
├── plugins/company-analysis/              # Codex デスクトップアプリのプラグインパッケージ本体
│   ├── plugin.json                        # ポータブルプラグインマニフェスト
│   ├── .codex-plugin/plugin.json          # Codex 互換プラグインマニフェスト
│   ├── assets/                            # プラグインUIアセット
│   └── skills/company-analysis/           # プラグイン内包スキル
├── .agents/plugins/marketplace.json       # Codex プラグインマーケットプレイスマニフェスト
├── .claude-plugin/                        # Claude Code プラグイン互換マニフェスト
├── install.sh                             # ワンライナーインストーラー
├── tools/validate.py                      # マニフェスト・リンク・スクリプト一括検証ツール
└── tests/test_company_analysis_plugin.py  # 自動テストスイート（unittest）
```

---

## 検証・テストの実行

```bash
python3 tools/validate.py
python3 tests/test_company_analysis_plugin.py
```

## ライセンス

[MIT License](LICENSE) © 2026 [HR0101](https://github.com/HR0101)
