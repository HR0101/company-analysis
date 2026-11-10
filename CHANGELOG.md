# 変更履歴 (Changelog)

このプロジェクトの主な変更点を記録します。

## [1.1.1] - 2026-11-11

### 修正 (Fixed)
- 質問の方向と件数を分離。応募者から企業への逆質問は標準10問、企業・面接官から応募者への想定質問は標準100問に変更。
- 入力UIに `interview_question_count`、レポート生成に `--interview-question-count` を追加。2種類の件数と省略指定を独立して反映。
- 想定質問は経歴・企業理解・職種・成果・協働など10テーマから構成し、約1分の自己紹介は引き続き出力。

## [1.1.0] - 2026-11-11

### 追加 (Added)
- ホストの質問UIで企業名・分析目的・5軸・出力形式を入力/選択するフロー。
- 選考対策の入力UIに逆質問の件数指定（標準100問・3問・5問・10問・100問・0問・自由入力）を追加。レポート生成の `--reverse-question-count` へ引き継ぎ、フル版・直前版の標準件数を100問へ統一。
- `scripts/input_ui.py`: 質問ツールの引数生成、回答済み条件の引き継ぎ、選択肢数が制限されたUIでの段階選択、テキスト質問へのフォールバック。
- `references/input-ui.md`: ツールの利用条件、回答の反映、無回答・キャンセル時の扱い。
- 会話履歴・提供済みの経歴に基づく約1分の自己紹介。作成手順と `--self-introduction-file` による原稿の引き継ぎ。
- 標準100問の逆質問を10テーマで作成する質問候補。
- 入力フローの回帰テスト。既存の検証に新規ファイルの配布コピー同期を追加。

### 変更・修正 (Changed / Fixed)
- 起動プロンプトを入力UI向けに変更。企業研究では採用関連項目を省き、内定比較は比較企業の入力へ分岐。
- 既存マーケットプレイス設定の保護・バックアップ・アトミック保存。
- 口コミの欠損指標やCFの符号だけに基づく断定を修正。
- 補足付きの面接フェーズ・第二新卒の判定、未知・曖昧なパターンの検出を改善。
- 企業研究と選考対策を分岐し、未確認・取得不可・非公開を区別。READMEの実行例を修正。

## [1.0.0] - 2026-04-12

### 追加 (Added)
- **Codex スキル＆プラグイン (`company-analysis`) の初回リリース**
  - ルート配置（1行 `git clone` 対応）、`skills/company-analysis/`（`$skill-installer` 対応）、`plugins/company-analysis/`（Codex / ChatGPT デスクトップアプリのプラグインマーケットプレイス対応）、`.claude-plugin/`（Claude Code プラグイン対応）のマルチレイアウト構成
  - `SKILL.md` および `agents/openai.yaml`（UIチップ・ブランドカラー・デフォルトプロンプト定義）
  - 5つの体系化リファレンスドキュメント（`references/`）:
    - `secrets-and-methodology.md`: 一次情報5大ソース（有価証券報告書・決算説明資料・中期経営計画・統合報告書・採用ピッチ資料）の読み解き方、統合報告書×OpenWork突合メソッド、仮説検証型逆質問の黄金公式
    - `industry-patterns.md`: 8大業界・25サブセクター別の収益構造、North Star KPI、2025-2026トレンド、競合比較軸
    - `role-patterns.md`: 6大職種・20専門ロール別の評価クライテリア、確認すべき業務KPI、面接官に刺さる逆質問
    - `interview-stage-patterns.md`: 6選考フェーズ（カジュアル面談・ES/職務経歴書・1次面接・2次面接・最終面接・内定後オファー面談）× 候補者属性（新卒/中途/第二新卒）× 企業タイプ（日系大手/メガベンチャー/未上場スタートアップ/外資系）別対策
    - `output-templates.md`: 完全版マスターシート、面接直前5分チートシート、内定比較意思決定マトリクス、ES・志望動機400字/3分トークスクリプトのテンプレート集
  - 3つのPython標準ライブラリ完結CLIツール（`scripts/`）:
    - `pattern_selector.py`: 5軸パターン一覧表示・日本語エイリアス解決・分析設計図（Blueprint）自動生成
    - `financial_analyzer.py`: 収益性・安全性・生産性・SaaS Rule of 40・キャッシュフロー8パターン自動診断・人的資本×OpenWorkギャップ診断
    - `report_generator.py`: `full` / `cheatsheet` / `offer-comparison` の3モード対応Markdownレポート生成
  - ワンライナーインストーラー (`install.sh`)、自動検証スクリプト (`tools/validate.py`)、単体テスト (`tests/test_company_analysis_plugin.py`)、GitHub Actions CI (`.github/workflows/validate.yml`)
