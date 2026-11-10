# 変更履歴 (Changelog)

このプロジェクトの主な変更点を記録します。

## [1.1.1] - 2026-04-12

### 変更・追加 (Changed & Added)
- **Codex ＆ Claude 完全統合リポジトリ (`company-analysis`) への統合**
  - 単一リポジトリ・単一ディレクトリ（`company-analysis`）で **Codex（CLI / ChatGPT・Codex デスクトップアプリ）** と **Claude（Claude Code / Claude デスクトップアプリ / Claude.ai Web）** の両方にネイティブ対応
  - Claude Code 公式プラグインマーケットプレイス（`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.claude-plugin/icon.png`）および Claude デスクトップアプリ直接アップロード用パッケージ（`dist/company-analysis-skill.zip`）を統合
  - 対話型入力UI（`scripts/input_ui.py` / `references/input-ui.md`）が Codex の `request_user_input_async` / `request_user_input` と Claude Code の `AskUserQuestion` の両方に対応
  - 会話履歴・提供資料に基づく約1分の自己紹介原稿の自動作成（`references/self-introduction.md`）、応募者から企業への逆質問（標準10問）と企業・面接官から応募者への想定質問（標準100問）の独立生成に対応
  - `install.sh` が1コマンドで Codex と Claude の両方（または `--codex` / `--claude` 個別指定）へインストール可能に

## [1.0.0] - 2026-04-12

### 追加 (Added)
- **企業分析スキル＆プラグイン (`company-analysis`) の初回リリース**
  - 一次情報5大ソース解読・統合報告書×OpenWork突合メソッド・5軸パターン選択・Python標準ライブラリ完結スクリプト群を公開
