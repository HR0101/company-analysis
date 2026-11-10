# コントリビューションガイド (Contributing)

`company-analysis` への改善提案・Issue・Pull Request を歓迎します。

## 変更手順

1. このリポジトリをフォークしてブランチを作成してください。
2. スキル定義（`SKILL.md`、`agents/openai.yaml`、`references/`、`scripts/`）を編集する場合は、以下の3箇所が同一内容になるよう同期し、さらに `dist/company-analysis-skill.zip` を再生成してください：
   - リポジトリルート（`./SKILL.md`, `./references/`, `./scripts/`, `./agents/`）
   - `./skills/company-analysis/`
   - `./plugins/company-analysis/skills/company-analysis/`

```bash
python3 tools/build_dist_zip.py
```

3. 変更後、以下の検証スクリプトとテストスイートを実行してすべて合格することを確認してください：

```bash
python3 tools/validate.py
python3 tests/test_company_analysis_plugin.py
```

## 品質基準

- `scripts/*.py` は外部パッケージに依存せず、**Python 3.9+ 標準ライブラリのみ**で動作すること。
- 財務数値やKPIを扱う際は、一次情報（有価証券報告書・決算説明資料・中期経営計画等）の出典と推測値を明確に区別する設計を維持すること。
- `SKILL.md` 内の相対リンクがすべて実在するファイルを指していること。
