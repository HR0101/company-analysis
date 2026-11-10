# セキュリティポリシー (Security Policy)

## サポート対象バージョン

現在、最新の `main` ブランチ（`1.1.x`）をサポートしています。

## 設計上のセキュリティ方針

- 同梱のPythonスクリプト（`scripts/pattern_selector.py`, `scripts/financial_analyzer.py`, `scripts/report_generator.py`）は**Python標準ライブラリのみ**で動作し、外部ネットワーク通信や外部パッケージの動的インストールを行いません。
- APIキー、認証情報、個人情報などをリポジトリ内に保存しません。

## 脆弱性の報告

セキュリティ上の問題を発見した場合は、公開Issueではなく GitHub の Security Advisories またはリポジトリオーナー（[@HR0101](https://github.com/HR0101)）へご連絡ください。
