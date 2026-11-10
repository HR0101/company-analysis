# 変更履歴 (Changelog)

このプロジェクトの主な変更点を記録します。

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
