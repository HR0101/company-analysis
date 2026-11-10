#!/usr/bin/env python3
"""
Pattern Selector & Blueprint Generator for Company Analysis Skill.

Supports:
- Listing all available patterns across 5 axes (--list)
- Fuzzy alias resolution (Japanese & English keywords)
- Generating a tailored Company Analysis & Interview Strategy Blueprint
  for any combination of:
    1. Industry (業界)
    2. Job Role (希望職種)
    3. Selection Stage / Interview Round (何次面接・選考フェーズ)
    4. Candidate Type (新卒 / 中途 / 第二新卒)
    5. Company Archetype (日系大手 / メガベンチャー / 未上場スタートアップ / 外資系)
"""

import argparse
import json
import re
import sys
import unicodedata
from typing import Dict, List, Optional, Tuple


INDUSTRY_PATTERNS: Dict[str, dict] = {
    "it-saas-web": {
        "name": "IT・SaaS・Web・AI・SIer業界",
        "aliases": [
            "it", "saas", "web", "ai", "sier", "システム", "ソフトウェア",
            "インターネット", "クラウド", "メガベンチャー", "通信",
        ],
        "business_model_focus": [
            "ストック収益（ARR/月額課金/保守）vs フロー収益（受託開発/初期導入）の比率",
            "商流上の立ち位置（プライム元請け比率 vs 二次・三次請け、グループ内販 vs 外販）",
            "プロダクト主導成長（PLG）か営業主導成長（SLG）か、マルチプロダクト展開の有無",
        ],
        "key_kpis": [
            "売上総利益率（粗利率：SaaSは70-85%、SIerは20-35%が目安）",
            "営業利益率とRule of 40（売上成長率＋営業利益率≧40%）",
            "ARR（年間経常収益）・NRR（売上継続率：110%以上が優良）・解約率（Churn Rate）",
            "プライム案件比率・1人あたり売上高/営業利益",
        ],
        "competitor_axes": [
            "ターゲット顧客層（エンタープライズ大企業 vs 中小SMB vs BtoCマス）",
            "強みを持つ業界ドメイン（金融・公共・製造・流通・クロスインダストリー）",
            "内製エンジニア比率と技術投資（R&D・AI実装・モダンアーキテクチャ）",
        ],
        "trend_themes": [
            "生成AIエージェントのプロダクト組み込みと価格モデルの変化（ID課金から成果/従量課金へ）",
            "単一SaaSからコンパウンドスタートアップ（マルチプロダクト統合）への移行",
            "レガシー基幹システムのモダナイゼーション（2025年の崖以降のクラウド移行・内製化支援）",
        ],
    },
    "consulting": {
        "name": "コンサルティング・シンクタンク業界",
        "aliases": [
            "consulting", "コンサル", "戦略コンサル", "総合コンサル",
            "itコンサル", "シンクタンク", "fas", "big4", "mbb",
        ],
        "business_model_focus": [
            "売上＝コンサルタント人数 × 稼働率（Utilization） × 単価（Charge-out Rate）",
            "戦略・構想策定（上流）からIT実装・BPO（保守運用）までのEnd-to-Endカバー範囲",
            "組織構造：ワンプール制（業界・領域横断アサイン）vs セクター/プラクティス縦割り制",
        ],
        "key_kpis": [
            "コンサルタント数・採用拡大ペース・離職率",
            "1人あたり売上高・稼働率（Utilization）",
            "戦略/業務案件とテクノロジー実装/マネージドサービス案件の売上構成比",
            "親密クライアント基盤（監査法人・銀行グループ・官公庁パイプ）",
        ],
        "competitor_axes": [
            "ワンプール制かインダストリー×コンピテンシーのセクター制か",
            "デリバリー・開発部隊の内製規模とテクノロジー実装力",
            "グローバルネットワークの一体運営度とカルチャー（Up or Out vs 協調育成）",
        ],
        "trend_themes": [
            "生成AIによるリサーチ・資料作成の自動化に伴う「提案だけコンサル」の淘汰と実装伴走へのシフト",
            "クライアント企業のDX内製化支援とジョイントベンチャー設立モデル",
            "人的資本経営・GX/サステナビリティ・経済安全保障（サプライチェーン再編）対応",
        ],
    },
    "manufacturing": {
        "name": "メーカー（製造業・電機・自動車・化学・食品・製薬等）",
        "aliases": [
            "manufacturing", "maker", "メーカー", "製造業", "電機", "自動車",
            "化学", "素材", "半導体", "食品", "化粧品", "製薬", "医薬品", "精密機器", "重工",
        ],
        "business_model_focus": [
            "BtoB（素材・部品・製造装置）かBtoC（完成品・消費財）か",
            "売り切り（フロー）＋ 保守・消耗品・アフターサービス（高利益ストック）のハイブリッド構造",
            "スマイルカーブ上の立ち位置（高収益な上流R&D/素材・下流サービスを握れているか）",
        ],
        "key_kpis": [
            "営業利益率（製造業平均5-8%、10%超は高付加価値、15%超は圧倒的Moat保有）",
            "海外売上高比率・地域別売上構成と為替感応度",
            "研究開発費（R&D）売上比率・設備投資額・減価償却費",
            "ROIC（投下資本利益率）とCCC（キャッシュ・コンバージョン・サイクル）",
        ],
        "competitor_axes": [
            "グローバルニッチトップ領域（世界シェアNo.1品目）の数と参入障壁",
            "事業ポートフォリオの集中と選択（コングロマリットか専業特化か）",
            "直販ソリューション営業か代理店・商社経由か、R&Dと事業部の連携速度",
        ],
        "trend_themes": [
            "モノ売りからコト売り（リカーリングモデル・稼働監視ソリューション）への転換",
            "半導体・EV・GX（脱炭素素材）・バイオ領域への大型投資とサプライチェーンの地政学リスク対応",
            "ROIC経営の徹底による低採算事業の売却・カーブアウトと高収益領域への集中",
        ],
    },
    "trading": {
        "name": "商社（総合商社・専門商社）",
        "aliases": [
            "trading", "shosha", "商社", "総合商社", "専門商社", "トレーディング",
        ],
        "business_model_focus": [
            "トレーディング（売買仲介・物流・与信・需給調整）× 事業投資（出資・経営参画・バリューチェーン構築）",
            "資源（エネルギー・金属）と非資源（食料・リテール・インフラ・化学品・機械）のポートフォリオ比率",
            "出資先企業へ経営人材を送り込み企業価値を引き上げるハンズオン機能",
        ],
        "key_kpis": [
            "当期純利益（総合商社における最重要指標）と基礎営業キャッシュフロー",
            "非資源分野の純利益比率（市況変動への耐性）",
            "ROE・ROIC（資本効率）とアセットリサイクル（資産入れ替え）実績",
            "専門商社の場合：売上総利益率・自己資本比率・親会社/特定メーカー依存度",
        ],
        "competitor_axes": [
            "セグメント別の強み（川上資源に強いか、川下リテール・食料・生活消費に強いか、電力・モビリティに強いか）",
            "人事制度（初期配属の部門別採用有無、若手の海外トレーニー・駐在時期、部門間異動の柔軟性）",
            "意思決定カルチャーと現場への権限委譲の度合い",
        ],
        "trend_themes": [
            "資源価格ボラティリティに左右されない非資源・川下バリューチェーンの強化",
            "エネルギートランジション（LNG・水素・アンモニア・再生可能エネルギー・蓄電池）への巨額投資",
            "専門商社における単なる仲介（中抜きリスク）からの脱却と加工・技術サポート・企画機能の強化",
        ],
    },
    "finance": {
        "name": "金融（銀行・証券・保険・カード・アセットマネジメント・FinTech）",
        "aliases": [
            "finance", "bank", "金融", "銀行", "メガバンク", "地銀", "証券",
            "投資銀行", "保険", "生保", "損保", "カード", "リース", "アセマネ", "fintech",
        ],
        "business_model_focus": [
            "資金利益（預貸利ザヤ・金利収入）vs 非資金利益（M&A・引受・資産運用・決済等の手数料収入）",
            "リテール（個人・富裕層ウェルスマネジメント）vs ホールセール（大企業・機関投資家・CIB）",
            "グループ総合力（銀行・信託・証券・リース・カードの連携モデル）",
        ],
        "key_kpis": [
            "銀行：連結業務純益・ROE・経費率（OHR）・海外収益比率・CET1比率",
            "証券・運用：預かり資産残高・AUM（運用資産残高）・ストック収入比率・リーグテーブル順位",
            "保険：修正純利益・ESR（経済価値ソルベンシー比率）・海外保険利益比率",
            "カード・リース：取扱高・営業債権残高・ROA・不良債権比率",
        ],
        "competitor_axes": [
            "グループ内の銀・信・証の連携体制と海外戦略（北米CIB・アジア商業銀行買収など）",
            "コース別・職種別採用（オープン採用）の専門性とキャリアパス",
            "デジタル金融サービス（BaaS・スーパーアプリ・法人DX）の顧客基盤",
        ],
        "trend_themes": [
            "「金利のある世界」への回帰に伴う国内預貸ビジネスの収益性変化と預金獲得競争",
            "貯蓄から投資へ（新NISA・富裕層ウェルスマネジメント・アセットマネジメント強化）",
            "非金融事業会社とのBaaS連携および生成AIによる審査・オペレーション高度化",
        ],
    },
    "media-ad-entertainment": {
        "name": "広告・メディア・エンタメ・ゲーム・コンテンツ業界",
        "aliases": [
            "media", "ad", "entertainment", "game", "広告", "メディア",
            "エンタメ", "ゲーム", "アニメ", "映画", "音楽", "出版", "テレビ",
        ],
        "business_model_focus": [
            "広告：マスメディア枠の手数料（コミッション）からデジタル広告運用・BX/DXコンサル（フィー）への転換",
            "エンタメ・ゲーム：自社IP（知的財産）の創出とメディアミックス（アニメ・ゲーム・グッズ・イベント・ライセンス）",
            "買い切り型（コンシューマー/映画興行）vs 継続課金型（ライブサービス/サブスク/ファンクラブ）",
        ],
        "key_kpis": [
            "広告：売上総利益（ネット粗利）・デジタル広告比率・非広告（DX/コンサル）売上比率",
            "ゲーム・エンタメ：営業利益率・IP別売上・海外売上高比率・リピート/カタログ販売比率・版権収入比率",
            "パイプライン（今後2〜3年の大型新作・イベント開発状況）",
        ],
        "competitor_axes": [
            "自社で強力なオリジナルIPを保有しているか（IPホルダー vs 受託制作/代理店）",
            "グローバル展開力（北米・欧州・アジアでの同時配信・ローカライズ・配給網）",
            "デジタル・データ活用力とクリエイターの創作環境のバランス",
        ],
        "trend_themes": [
            "広告代理店の「統合マーケティング×DXコンサルティングファーム化」",
            "日本発IP（アニメ・ゲーム・キャラクター）のグローバルマネタイズと実写化・テーマパーク展開",
            "開発費高騰に対するマルチプラットフォーム展開と生成AIの制作パイプライン活用",
        ],
    },
    "real-estate-infra-logistics": {
        "name": "不動産・デベロッパー・建設・インフラ・エネルギー・物流業界",
        "aliases": [
            "realestate", "developer", "infra", "logistics", "不動産", "デベロッパー",
            "ゼネコン", "建設", "ハウスメーカー", "インフラ", "電力", "ガス", "鉄道", "航空", "海運", "物流",
        ],
        "business_model_focus": [
            "デベロッパー：賃貸ストック収益（オフィス・商業・物流）× 開発分譲・機関投資家への物件売却（アセット回転型フロー）",
            "鉄道・インフラ：インフラ利用料（運輸・電力・ガス）＋ 沿線/周辺不動産・商業・ホテル等の多角化収益",
            "莫大な初期設備投資（CAPEX）を長期の安定キャッシュフローで回収するバランスシート経営",
        ],
        "key_kpis": [
            "セグメント別営業利益構成（賃貸 vs 分譲売却、運輸 vs 不動産など）",
            "含み益（賃貸等不動産の時価−簿価）・空室率・D/Eレシオ（有利子負債倍率）",
            "海外事業利益比率と大型再開発パイプライン（2030年代までの竣工予定案件）",
        ],
        "competitor_axes": [
            "強みを持つ地盤エリア（丸の内・日本橋・渋谷・六本木・新宿・品川・梅田等）と街づくりの思想",
            "アセットポートフォリオ（オフィス偏重か、商業・ホテル・アリーナ・物流・住宅・海外の多角化か）",
            "少数精鋭のプロジェクトマネジメント力（デベロッパーは従業員数百〜千数百人で数千億円の利益を出す）",
        ],
        "trend_themes": [
            "金利上昇局面における不動産キャップレート・資金調達コスト管理と高付加価値オフィスへの二極化",
            "データセンター・半導体工場・自動化物流施設・GX（脱炭素ビル・再エネ）開発需要の急拡大",
            "インバウンド観光需要の取り込みと地方・海外都市開発への展開",
        ],
    },
    "hr-retail-service-healthcare": {
        "name": "人材・教育・小売・流通・EC・医療ヘルスケア・サービス業界",
        "aliases": [
            "hr", "retail", "service", "healthcare", "人材", "教育", "小売",
            "流通", "アパレル", "ec", "百貨店", "コンビニ", "医療", "ヘルスケア", "介護", "サービス",
        ],
        "business_model_focus": [
            "人材：人材紹介（年収×30-35%の成功報酬：両面型 vs 分業型）・求人広告（掲載/応募課金）・人材派遣（稼働マージン）・HRテックSaaS",
            "小売・流通：SPA（企画〜製造〜販売の垂直統合で高粗利）vs 仕入販売・フランチャイズロイヤリティ・EC/OMO",
            "労働集約になりやすい構造をテクノロジー・PB開発・プラットフォーム化でどう高収益化しているか",
        ],
        "key_kpis": [
            "人材：コンサルタント1人あたり売上・RA/CA体制・HRテック比率・営業利益率",
            "小売・EC：既存店売上高前年比（客数×客単価）・売上総利益率（PB比率・値引き率）・在庫回転日数・EC化率",
            "海外店舗数・海外売上比率と店舗あたり収益性",
        ],
        "competitor_axes": [
            "人材：両面型（一気通貫）か片面型（分業）か、ハイクラス/若手/業界特化のポジショニング",
            "小売：サプライチェーンの自前化度合い（SPA）、店舗立地戦略、アプリ会員経済圏の強さ",
            "現場店長・SV・キャリアアドバイザーの評価制度とキャリアパスの多様性",
        ],
        "trend_themes": [
            "構造的な人手不足・転職市場の活況に伴うダイレクトリクルーティング・リスキリング・人的資本投資の拡大",
            "小売におけるインフレ下の価格転嫁力（PB商品開発力）と越境EC・アジア/北米出店加速",
            "医療・介護・ヘルスケア領域のDX（オンライン診療・薬局DX・医療従事者紹介プラットフォーム）",
        ],
    },
}

ROLE_PATTERNS: Dict[str, dict] = {
    "sales-cs": {
        "name": "営業・カスタマーサクセス系（法人営業/個人営業/IS/FS/CS）",
        "aliases": [
            "sales", "cs", "営業", "法人営業", "個人営業", "ソリューション営業",
            "インサイドセールス", "フィールドセールス", "カスタマーサクセス", "代理店営業",
        ],
        "checkpoints": [
            "商材の性質（有形 vs 無形）と単価・受注リードタイム（即決型 vs 数ヶ月〜数年の大型案件）",
            "営業組織の体制（The Model型のIS/FS/CS分業か、一気通貫型か）",
            "新規開拓（Hunting）と既存深耕・アカウント営業（Farming）の比率",
            "直販（ダイレクト）か代理店・パートナー経由（チャネルセールス）か",
            "KPI設計とインセンティブ・評価制度（個人数字重視かチーム・プロセス重視か）",
        ],
        "reproducibility_proof": "「顧客の表面的な要望の奥にある潜在課題（真のボトルネック）を仮説立てて引き出し、社内外の関係者を巻き込んで解決策を実行・数値成果に繋げた再現性」",
        "reverse_questions": [
            "御社が現在注力されている〇〇領域の拡大において、営業（またはCS）現場が顧客から最も多く直面する導入障壁（ボトルネック）は何でしょうか？",
            "御社の営業組織でトップパフォーマーとして活躍されている方に共通する『商談前の仮説準備』や『他部署（開発やマーケ）の巻き込み方』の特徴を伺いたいです。",
        ],
    },
    "planning-marketing-bizdev": {
        "name": "企画・マーケティング・事業開発系（経営企画/事業企画/商品企画/マーケ/BizDev）",
        "aliases": [
            "planning", "marketing", "bizdev", "企画", "経営企画", "事業企画",
            "商品企画", "マーケティング", "マーケ", "事業開発", "新規事業", "広報",
        ],
        "checkpoints": [
            "企画・マーケ部門がP/L責任（損益・予算決定権）をどこまで持っているか",
            "主戦場がBtoCブランドマーケか、デジタル獲得（グロース）か、BtoBリード獲得か",
            "企画の武器となる自社独自データ・顧客基盤・アセットの強さ",
            "新規事業（BizDev）創出制度の実績と撤退・継続投資の判断基準",
            "初期配属のリアル（新卒1年目から企画配属があるか、現場営業経験後の異動が前提か）",
        ],
        "reproducibility_proof": "「定量データ（数字の異常値）と定性インサイト（顧客・現場の観察）を往復して勝ち筋の仮説を立て、直接の指揮権がない他部署（開発・営業等）を動かして施策を完遂した再現性」",
        "reverse_questions": [
            "御社は〇〇という強力な顧客データ・アセットをお持ちですが、現在のマーケティング（または事業企画）において、今後さらに活用余地が大きいとお考えの領域はどこでしょうか？",
            "新しい施策や新規事業を推進する際、社内の営業部門や開発部門と合意形成する上で最も重視されている判断基準（KPIや顧客価値指標）は何でしょうか？",
        ],
    },
    "pdm-pm-consultant": {
        "name": "PdM・PM・コンサルタント系（プロダクトマネージャー/PM/コンサル/プリセールス）",
        "aliases": [
            "pdm", "pm", "consultant", "プロダクトマネージャー", "プロジェクトマネージャー",
            "コンサルタント", "プリセールス", "セールスエンジニア", "itアーキテクト",
        ],
        "checkpoints": [
            "対象プロダクト/事業のフェーズ（0→1のPMF模索期か、1→10の成長期か、10→100の基盤統合期か）",
            "PdMの意思決定権限（「何を作らないか」を決める権限があるか、大口顧客の受託開発化していないか）",
            "PMの商流（プライム元請けとして要件定義から握るか）と開発手法（アジャイル vs ウォーターフォール）",
            "コンサルタントの関与範囲（構想策定のみか、業務定着・システム実装まで一気通貫か）",
            "エンジニア・デザイナー・ビジネスサイドとの組織力学",
        ],
        "reproducibility_proof": "「複雑に絡み合う課題や相反するステークホルダーの要求（QCDや短期売上vs中長期基盤）を構造化し、解くべきセンターピン（本質的イシュー）を特定してプロジェクトを推進した再現性」",
        "reverse_questions": [
            "現在事業が拡大する中で、『短期的な大口顧客の個別要望への対応』と『中長期的なプロダクトの汎用性・基盤強化』のトレードオフをどのような基準で意思決定されていますか？",
            "御社のPM/PdM（またはコンサルタント）として、単なる進行管理にとどまらず一段高いバリューを発揮している方に共通する視座やスキルは何でしょうか？",
        ],
    },
    "software-ai-engineer": {
        "name": "ソフトウェア・AI・データエンジニア系（Web/モバイル/AI/DS/SRE/セキュリティ）",
        "aliases": [
            "software", "engineer", "swe", "ai-engineer", "data", "sre", "エンジニア",
            "ソフトウェアエンジニア", "webエンジニア", "aiエンジニア", "データサイエンティスト", "インフラエンジニア",
        ],
        "checkpoints": [
            "エンジニアリング組織の位置づけ（競争優位の源泉となるProfit Centerか、外注管理中心か）",
            "技術スタックのモダンさと、技術的負債解消・リファクタリングへの投資比率",
            "内製化率と開発プロセス（エンジニアが仕様策定のWhyから関われるスクラム体制か）",
            "AI・LLMの開発環境活用およびプロダクトへの実装フェーズ（PoC止まりか本番運用か）",
            "評価制度・技術グレード（EM管理職だけでなくIC/Tech Lead/Principalとして報われるデュアルラダーか）",
        ],
        "reproducibility_proof": "「単なる実装経験ではなく、ビジネス要件・非機能要件（性能・保守性・コスト）の制約下で『なぜその技術・設計を選んだか（トレードオフの判断）』を説明でき、チーム開発の生産性や事業KPIを改善した再現性」",
        "reverse_questions": [
            "御社のテックブログで〇〇の取り組みを拝見しました。現在、トラフィックや組織がさらに拡大する中で直面している最大の技術的ボトルネックや、今後1〜2年で解消したい技術的負債は何でしょうか？",
            "エンジニアが仕様策定のどの段階からPdMやビジネスサイドと関わるカルチャーでしょうか？エンジニア起点の提案からプロダクトに実装された事例があれば伺いたいです。",
        ],
    },
    "rd-manufacturing-eng": {
        "name": "研究開発（R&D）・機電・化学・生産技術系",
        "aliases": [
            "rd", "research", "研究開発", "研究職", "設計", "機械設計", "電気設計",
            "化学", "生産技術", "品質管理", "品質保証", "知財", "機電",
        ],
        "checkpoints": [
            "R&D組織の階層（5〜10年先の全社研究所か、1〜3年先の事業部開発部隊か）",
            "研究シーズを事業化する仕組み（「死の谷」を越えるマーケ・生産技術との連携体制）",
            "研究開発費率と知財（特許・ノウハウ秘匿・オープンイノベーション）戦略",
            "生産技術・マザー工場の自動化（スマートファクトリー・AI検査）投資状況",
            "研究所・工場の立地とローテーション・海外赴任の機会",
        ],
        "reproducibility_proof": "「専門外の面接官にも研究の意義を1分で噛み砕いて伝える抽象化力と、『仮説→実験→予想外の失敗→原因究明→アプローチ再設計』という科学的課題解決プロセスの再現性」",
        "reverse_questions": [
            "中期経営計画で〇〇領域へのR&D投資を強化されると拝見しました。現在のコア技術をその新領域へ社会実装・量産化するにあたり、現在最大の技術的ハードルとなっているのはどのような点でしょうか？",
            "研究開発（または生産技術）部門の若手社員が、顧客の現場や営業部門と直接対話してニーズを拾い上げる機会はどの程度ありますか？",
        ],
    },
    "corporate": {
        "name": "コーポレート・管理部門系（経理財務/人事HR/法務/広報IR/情シス）",
        "aliases": [
            "corporate", "accounting", "finance-corp", "hr-corp", "legal", "pr", "ir",
            "コーポレート", "管理部門", "経理", "財務", "人事", "法務", "総務", "広報", "情報システム",
        ],
        "checkpoints": [
            "コーポレート部門の役割期待（定型業務の正確な処理か、経営・事業部に伴走するBP：ビジネスパートナーか）",
            "企業の成長フェーズ固有の課題（IPO準備・J-SOX、海外M&A後のPMI、ROIC経営導入、人的資本開示高度化）",
            "ルーティン業務のBPO・SaaS化・DX進行度",
            "経営陣（CFO/CHRO/CLO）との距離感と提案裁量",
            "ジョブローテーションの有無と専門キャリアの深化パス",
        ],
        "reproducibility_proof": "「高い正確性・法令遵守意識をベースに持ちながら、『ルールだからできない』で止めず『事業の成長目的を達成するためにどうリスクを制御して実現するか（How to Enable）』を設計・交渉した再現性」",
        "reverse_questions": [
            "御社が中期経営計画で掲げる事業ポートフォリオ変革（またはM&A・グローバル展開・人的資本経営）を推進する上で、現在コーポレート部門（経理/人事/法務等）として最も強化が急務となっているテーマは何でしょうか？",
            "守りのガバナンスと攻めの事業スピードを両立させる上で、御社のコーポレート部門が事業部と関わる際に最も大切にされているスタンスを伺いたいです。",
        ],
    },
}

STAGE_PATTERNS: Dict[str, dict] = {
    "casual-intern-ob": {
        "name": "インターン・OB/OG訪問・カジュアル面談（情報収集・早期接点）",
        "aliases": ["0", "casual", "intern", "ob", "og", "インターン", "カジュアル面談", "ob訪問", "座談会"],
        "interviewer_persona": "現場社員・リクルーター・人事採用担当",
        "core_objective": "「選考ではない」という言葉を鵜呑みにせず、仮説を持った質問で知的好奇心と準備の深さを示し、本選考の2次・最終面接で武器になる『現場の一次情報（生の声）』を回収する。",
        "analysis_depth": "4W1Hビジネスモデル＋直近のニュース1〜2件＋競合1〜2社との違いの仮説（15〜30分レベルの骨格把握）",
        "pass_strategy": [
            "HPを読めばわかる質問（「御社の強みは？」等）は絶対にせず、「私は〇〇だと調べて仮説を持ったのですが、現場の実感はいかがですか？」と聞く。",
            "本選考の志望動機で使えるキラーフレーズ（「なぜ競合A社ではなくこの会社を選んだのか」「入社前後のギャップ」「活躍している人の共通点」）を聞き出す。",
        ],
    },
    "es-resume": {
        "name": "書類選考・ES（エントリーシート）・職務経歴書作成",
        "aliases": ["1", "es", "resume", "cv", "書類", "エントリーシート", "履歴書", "職務経歴書"],
        "interviewer_persona": "人事スクリーニング担当・現場採用マネージャー（閲覧時間30〜60秒）",
        "core_objective": "流し読みされる30秒間で『結論ファースト』『定量的な実績・行動プロセス』『企業が求める人物像キーワードとの一致』を一目で伝え、面接に呼ぶ理由を作る。",
        "analysis_depth": "求める人物像の行動特性キーワード3つの抽出 ＋ 競合他社と差別化された『なぜ御社か』の1〜2文凝縮",
        "pass_strategy": [
            "志望動機は『①成し遂げたい軸（結論）→ ②原体験 → ③なぜこの業界・その中でもなぜ御社か（独自戦略・強み）→ ④自分の強みを活かした入社後の貢献』の黄金4段構成にする。",
            "ガクチカや職務経歴書には、単なる結果だけでなく『どんな課題に対し、なぜその打ち手を考え、どう周囲を巻き込んだか（再現性のプロセス）』を企業のバリューに合わせて記述する。",
        ],
    },
    "first-interview": {
        "name": "1次面接（人事・若手〜中堅現場社員面接）",
        "aliases": ["2", "1st", "first", "first-interview", "一次面接", "1次面接", "初期面接"],
        "interviewer_persona": "人事担当者、または若手〜中堅の現場社員（入社3〜8年目クラス）",
        "core_objective": "『減点ゼロ（足切り回避）』＋『基礎的な事業理解の正確さ』＋『結論ファーストで端的な会話のキャッチボールと素直さ・協働性』の証明。",
        "analysis_depth": "主力事業・収益源の正確な理解 ＋ 求める人物像へのフィット ＋ 志望職種の現場業務イメージ",
        "pass_strategy": [
            "1回の回答は45秒〜1分以内（結論＋理由1〜2文）に収め、長広舌を避けて会話のテンポを最優先する。",
            "難しいIR数値や経営批判を上から目線で語るのではなく、『御社の〇〇事業が顧客の△△を解決している点に魅力を感じ、現場でこう貢献したい』と真っ直ぐ熱意を伝える。",
            "逆質問は若手〜中堅社員が自分の実体験から答えやすい『入社後の立ち上がり方・仕事のやりがい・チームの雰囲気』を中心に聞く。",
        ],
    },
    "second-interview": {
        "name": "2次・中盤面接（現場課長・部長・マネージャー面接）",
        "aliases": ["3", "2nd", "second", "second-interview", "二次面接", "2次面接", "三次面接", "3次面接", "中盤面接", "現場面接"],
        "interviewer_persona": "配属予定部門の課長・部長・マネージャー・テックリード（実質的な合否決定権者）",
        "core_objective": "『自分の部署に配属したら実務で成果を出せるか（再現性）』と『なぜ競合他社ではなく自社なのか（論理的納得感）』の完全証明。",
        "analysis_depth": "競合2〜3社との徹底比較マトリクス ＋ 中期経営計画における志望部門のミッション・課題仮説 ＋ 職種別の具体業務解像度",
        "pass_strategy": [
            "『なぜこの行動をとったのか？』『他の選択肢はなかったのか？』というWhyの5回深掘りに論理的に答えられるよう、自分の過去の経験を構造化しておく。",
            "競合他社名を具体的に挙げた上で、『A社は〇〇、B社は△△に強みがある一方、御社は□□という独自の強み・戦略があるため、私の目指す××と最も合致する』と言い切る。",
            "逆質問では、中計や決算説明資料の事実を引用しつつ、『現在現場レベルでどんな課題やボトルネックがあるか』『どんな人材に重要案件を任せたいか』をぶつける。",
        ],
    },
    "final-interview": {
        "name": "最終面接・役員面接（社長・取締役・事業本部長面接）",
        "aliases": ["4", "final", "final-interview", "executive", "最終面接", "役員面接", "社長面接"],
        "interviewer_persona": "代表取締役社長（CEO）・担当役員・事業本部長・人事統括責任者（CHRO）",
        "core_objective": "『内定を出したら必ず入社する覚悟・第一志望度』＋『経営理念（VMV）と人生の原体験の深い一致』＋『5〜10年後の会社の未来像と自身のキャリアビジョンの重なり』の証明。",
        "analysis_depth": "統合報告書のCEOメッセージ・創業の精神・中期経営計画の長期ビジョン・有価証券報告書の経営課題の完全掌握",
        "pass_strategy": [
            "スキル自慢ではなく、『なぜ自分の人生においてこの領域に情熱を注ぐのか（原体験）』と『企業のミッション・長期ビジョン』を一本の線で繋げて語る。",
            "『他社選考状況は？』『うちが第一志望か？』に対して、就活/転職の軸が一貫した他社名を挙げつつ、なぜその軸において御社がNo.1なのかを論理と熱量で即答する。",
            "逆質問では、社長・役員の視座に合わせた『長期ビジョン達成に向けた最大の勝負どころ』『絶対に守り抜くべき企業のDNA』『次代のリーダーに求める覚悟』を問う。",
        ],
    },
    "offer-comparison": {
        "name": "内定後・オファー面談・複数社内定比較（承諾意思決定）",
        "aliases": ["5", "offer", "offer-comparison", "内定", "オファー面談", "条件面談", "内定比較", "承諾"],
        "interviewer_persona": "人事採用責任者・配属先部長・および意思決定者としての自分自身",
        "core_objective": "『選ばれる側』から『選ぶ側』へ視点を切り替え、初期配属・実質総報酬・評価基準・組織の健全性（統合報告書×口コミギャップ）を検証して後悔のない意思決定を行う。",
        "analysis_depth": "財務安全性・将来性 ＋ OpenWork等の8指標チャート形状と統合報告書の人的資本データ突合 ＋ 3〜5年後の市場価値シミュレーション",
        "pass_strategy": [
            "オファー面談では、額面年収だけでなく『固定残業代の時間数と超過支給』『賞与の変動幅』『住宅手当・福利厚生』『初期配属部署と最初の半年間の期待目標（ミッション）』を具体的に確認する。",
            "複数社内定で迷った場合は、知名度や初任給の多寡だけでなく『3〜5年後にどんな職務経歴書が書けるか（市場価値）』を含む5軸100点満点スコアカードで客観評価する。",
        ],
    },
}

CANDIDATE_PATTERNS: Dict[str, dict] = {
    "new-grad": {
        "name": "新卒就活（学部・修士・博士）",
        "aliases": ["new-grad", "newgrad", "shinsotsu", "新卒", "就活", "学生", "大学院生"],
        "focus": "ポテンシャル・素直さ・原体験と志望軸の一貫性・カルチャーフィット・長期育成環境と配属リスクの確認",
    },
    "mid-career": {
        "name": "中途採用・経験者転職",
        "aliases": ["mid-career", "mid", "tenshoku", "中途", "転職", "経験者", "キャリア採用"],
        "focus": "即戦力としてのスキル再現性・当該ポジションの募集背景（組織課題）の特定・処遇と裁量権のすり合わせ",
    },
    "second-new-grad": {
        "name": "第二新卒・既卒・キャリアチェンジ",
        "aliases": ["second-new-grad", "second", "第二新卒", "既卒", "キャリアチェンジ", "未経験転職"],
        "focus": "早期離職・転換理由のポジティブ変換（他責にしない一貫した成長目的）・基礎ビジネススキル＋高い吸収力の証明",
    },
}

ARCHETYPE_PATTERNS: Dict[str, dict] = {
    "listed-enterprise": {
        "name": "日系大手・上場企業",
        "aliases": ["listed-enterprise", "enterprise", "jtc", "listed", "大手", "日系大手", "上場企業"],
        "primary_sources": [
            "① 有価証券報告書（【事業の内容】【対処すべき課題】【事業等のリスク】【従業員の状況】【セグメント情報】）",
            "② 決算説明資料（直近通期・四半期の業績ハイライト・KPI推移・質疑応答）",
            "③ 中期経営計画（3〜5年後の定量目標・重点投資領域・ポートフォリオ改革）",
            "④ 統合報告書（CEOメッセージ・価値創造プロセス・人的資本データ）＋ OpenWork突合",
        ],
    },
    "mega-venture": {
        "name": "メガベンチャー・急成長上場IT",
        "aliases": ["mega-venture", "megaventure", "メガベンチャー", "上場ベンチャー", "グロース上場"],
        "primary_sources": [
            "① 決算説明資料・中期経営計画（ARR/GMV等のKPI推移、既存祖業と新規投資事業のバランス）",
            "② カルチャーデック・採用ピッチ資料（MVV・行動規範バリューの『称賛される行動／NG行動』）",
            "③ 有価証券報告書（従業員数の増加ペース・平均年齢・セグメント別損益）",
            "④ 社員note・テックブログ・OpenWork（『20代成長環境』と『待遇・法令順守』のバランス確認）",
        ],
    },
    "startup-unlisted": {
        "name": "未上場スタートアップ・ベンチャー企業",
        "aliases": ["startup-unlisted", "startup", "venture", "unlisted", "スタートアップ", "ベンチャー", "未上場"],
        "primary_sources": [
            "① 採用ピッチ資料（Speaker Deck / Notion：TAM・SAM・SOM、プロダクト優位性、評価制度、組織課題）",
            "② PR TIMES・INITIAL・STARTUP DB（資金調達ラウンド、累計調達額、リードVC・事業会社株主の顔ぶれ）",
            "③ 官報決算公告（純資産・利益剰余金・黒字/先行投資赤字の規模）",
            "④ 創業者（CEO/CTO）インタビュー・X/note・Wantedly（Founder-Market Fitと採用ペルソナ）",
        ],
    },
    "foreign-affiliated": {
        "name": "外資系企業（コンサル・IT・金融・メーカー）",
        "aliases": ["foreign-affiliated", "foreign", "gaishi", "外資", "外資系"],
        "primary_sources": [
            "① グローバル本社 Annual Report / Form 10-K（全社戦略・地域別売上・R&D投資）",
            "② 日本法人（Japanオフィス）の公式リリース・代表インタビュー（日本拠点のミッション：営業拠点か開発・企画拠点か）",
            "③ Job Description（JD：職務記述書）のResponsibilitiesとQualificationsの1行ずつの分解",
            "④ OpenWork・Glassdoor・現役社員リンクトイン（Up or Outの厳しさ、評価KPI、英語使用頻度）",
        ],
    },
}


def resolve_pattern(query: str, catalog: Dict[str, dict], default_key: str) -> str:
    if not query or not query.strip():
        return default_key
    q = unicodedata.normalize("NFKC", query).strip().lower()
    if q in catalog:
        return q
    exact = {
        key for key, data in catalog.items()
        if q in [unicodedata.normalize("NFKC", a).lower() for a in data.get("aliases", [])]
        or q == unicodedata.normalize("NFKC", data["name"]).lower()
    }
    if len(exact) == 1:
        return exact.pop()
    if len(exact) > 1:
        raise ValueError(f"曖昧なパターン {query!r}: IDを指定してください ({', '.join(sorted(exact))})")

    # Prefer specific phrases (第二新卒 over 新卒). Menu numbers are exact-only;
    # Latin abbreviations must have boundaries, so 'it' cannot match 'retail'.
    matches = []
    for key, data in catalog.items():
        for token in [key, data["name"], *data.get("aliases", [])]:
            token = unicodedata.normalize("NFKC", token).lower()
            if token.isdigit():
                continue
            if token.isascii():
                matched = re.search(r"(?<![a-z0-9])" + re.escape(token) + r"(?![a-z0-9])", q)
            else:
                matched = token in q
            if matched:
                matches.append((key, token))
    if matches:
        # Ignore a generic token only when a more specific matched phrase contains
        # it. Independent alternatives remain ambiguous even at different lengths.
        winners = sorted({
            key for key, token in matches
            if not any(token != other and token in other for _, other in matches)
        })
        if len(winners) == 1:
            return winners[0]
        raise ValueError(f"曖昧なパターン {query!r}: IDを指定してください ({', '.join(winners)})")
    raise ValueError(f"未知のパターン {query!r}: 有効なIDは {', '.join(catalog)}")


def build_blueprint(
    company: str,
    industry_key: str,
    role_key: str,
    stage_key: str,
    candidate_key: str,
    archetype_key: str,
    competitors: List[str],
) -> dict:
    ind = INDUSTRY_PATTERNS[industry_key]
    role = ROLE_PATTERNS[role_key]
    stage = STAGE_PATTERNS[stage_key]
    cand = CANDIDATE_PATTERNS[candidate_key]
    arch = ARCHETYPE_PATTERNS[archetype_key]

    comp_list = competitors if competitors else ["競合A社（業界首位クラス）", "競合B社（同規模・隣接領域）"]

    return {
        "target_company": company or "対象企業",
        "competitors": comp_list,
        "selected_patterns": {
            "industry": {"id": industry_key, "name": ind["name"]},
            "role": {"id": role_key, "name": role["name"]},
            "stage": {"id": stage_key, "name": stage["name"]},
            "candidate": {"id": candidate_key, "name": cand["name"]},
            "archetype": {"id": archetype_key, "name": arch["name"]},
        },
        "step1_primary_sources": arch["primary_sources"],
        "step2_industry_analysis": {
            "business_model_focus": ind["business_model_focus"],
            "key_kpis": ind["key_kpis"],
            "competitor_axes": ind["competitor_axes"],
            "trend_themes": ind["trend_themes"],
        },
        "step3_role_analysis": {
            "operational_checkpoints": role["checkpoints"],
            "reproducibility_proof": role["reproducibility_proof"],
            "role_reverse_questions": role["reverse_questions"],
        },
        "step4_stage_strategy": {
            "interviewer_persona": stage["interviewer_persona"],
            "core_objective": stage["core_objective"],
            "required_analysis_depth": stage["analysis_depth"],
            "pass_strategy": stage["pass_strategy"],
        },
        "step5_candidate_adjustment": cand["focus"],
    }


def format_blueprint_markdown(bp: dict) -> str:
    sp = bp["selected_patterns"]
    comp_str = " / ".join(bp["competitors"])
    lines = [
        f"# 🧭 企業分析＆選考対策ブループリント：{bp['target_company']}",
        "",
        "## 1. 選択された分析パターン（5軸設定）",
        f"- **対象企業**: {bp['target_company']} （比較競合: {comp_str}）",
        f"- **① 業界パターン**: `{sp['industry']['id']}` — {sp['industry']['name']}",
        f"- **② 希望職種パターン**: `{sp['role']['id']}` — {sp['role']['name']}",
        f"- **③ 選考フェーズ（何次面接か）**: `{sp['stage']['id']}` — {sp['stage']['name']}",
        f"- **④ 応募者属性**: `{sp['candidate']['id']}` — {sp['candidate']['name']}",
        f"- **⑤ 企業タイプ**: `{sp['archetype']['id']}` — {sp['archetype']['name']}",
        "",
        "---",
        "",
        "## 2. 最優先で当たるべき一次情報ルート（企業タイプ別）",
    ]
    for src in bp["step1_primary_sources"]:
        lines.append(f"- {src}")

    lines.extend([
        "",
        f"## 3. 業界別・深掘りチェックポイント（{sp['industry']['name']}）",
        "### ビジネスモデル・収益構造の着眼点",
    ])
    for item in bp["step2_industry_analysis"]["business_model_focus"]:
        lines.append(f"- {item}")

    lines.append("\n### 必ず確認すべき重要KPI・財務指標")
    for item in bp["step2_industry_analysis"]["key_kpis"]:
        lines.append(f"- {item}")

    lines.append(f"\n### 競合他社（{comp_str}）との比較軸")
    for item in bp["step2_industry_analysis"]["competitor_axes"]:
        lines.append(f"- {item}")

    lines.append("\n### 面接で語ると差がつく業界トレンド・構造課題")
    for item in bp["step2_industry_analysis"]["trend_themes"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        f"## 4. 希望職種別・業務解像度チェックポイント（{sp['role']['name']}）",
        "### 調べるべき5つの業務リアル",
    ])
    for item in bp["step3_role_analysis"]["operational_checkpoints"]:
        lines.append(f"- {item}")

    lines.extend([
        "",
        "### 面接官に証明すべき「再現性（Why Me）」の核",
        f"- {bp['step3_role_analysis']['reproducibility_proof']}",
        "",
        f"## 5. 選考フェーズ別・突破戦略（{sp['stage']['name']}）",
        f"- **想定される評価者（面接官）**: {bp['step4_stage_strategy']['interviewer_persona']}",
        f"- **合格の核心（センターピン）**: {bp['step4_stage_strategy']['core_objective']}",
        f"- **求められる企業分析の深さ**: {bp['step4_stage_strategy']['required_analysis_depth']}",
        f"- **応募区分（{sp['candidate']['name']}）の重点ポイント**: {bp['step5_candidate_adjustment']}",
        "",
        "### このフェーズの具体的アクション・注意点",
    ])
    for item in bp["step4_stage_strategy"]["pass_strategy"]:
        lines.append(f"- {item}")

    lines.append("\n### 職種×フェーズ特化のキラー逆質問ベース")
    for q in bp["step3_role_analysis"]["role_reverse_questions"]:
        lines.append(f"- 「{q}」")

    return "\n".join(lines) + "\n"


def list_all_patterns_markdown() -> str:
    lines = [
        "# 📚 利用可能な企業分析パターン一覧（全5軸）",
        "",
        "## ① 業界パターン (`--industry`)",
    ]
    for k, v in INDUSTRY_PATTERNS.items():
        lines.append(f"- `{k}`: **{v['name']}** (キーワード例: {', '.join(v['aliases'][:5])})")

    lines.append("\n## ② 希望職種パターン (`--role`)")
    for k, v in ROLE_PATTERNS.items():
        lines.append(f"- `{k}`: **{v['name']}** (キーワード例: {', '.join(v['aliases'][:5])})")

    lines.append("\n## ③ 選考フェーズ・何次面接かパターン (`--stage`)")
    for k, v in STAGE_PATTERNS.items():
        lines.append(f"- `{k}`: **{v['name']}** (評価者: {v['interviewer_persona']})")

    lines.append("\n## ④ 応募者属性パターン (`--candidate`)")
    for k, v in CANDIDATE_PATTERNS.items():
        lines.append(f"- `{k}`: **{v['name']}** — {v['focus']}")

    lines.append("\n## ⑤ 企業タイプパターン (`--archetype`)")
    for k, v in ARCHETYPE_PATTERNS.items():
        lines.append(f"- `{k}`: **{v['name']}**")

    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(
        description="Company Analysis Pattern Selector & Blueprint Generator"
    )
    parser.add_argument("--list", action="store_true", help="List all available patterns across 5 axes")
    parser.add_argument("--company", default="", help="Target company name")
    parser.add_argument("--industry", default="it-saas-web", help="Industry pattern ID or Japanese keyword")
    parser.add_argument("--role", default="sales-cs", help="Job role pattern ID or Japanese keyword")
    parser.add_argument("--stage", default="first-interview", help="Selection stage pattern ID or keyword (e.g. 1次面接, 2次面接, 最終面接)")
    parser.add_argument("--candidate", default="new-grad", help="Candidate type (new-grad, mid-career, second-new-grad)")
    parser.add_argument("--archetype", default="listed-enterprise", help="Company archetype (listed-enterprise, mega-venture, startup-unlisted, foreign-affiliated)")
    parser.add_argument("--competitors", default="", help="Comma-separated competitor names")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")

    args = parser.parse_args()

    if args.list:
        if args.format == "json":
            print(json.dumps({
                "industries": {k: v["name"] for k, v in INDUSTRY_PATTERNS.items()},
                "roles": {k: v["name"] for k, v in ROLE_PATTERNS.items()},
                "stages": {k: v["name"] for k, v in STAGE_PATTERNS.items()},
                "candidates": {k: v["name"] for k, v in CANDIDATE_PATTERNS.items()},
                "archetypes": {k: v["name"] for k, v in ARCHETYPE_PATTERNS.items()},
            }, ensure_ascii=False, indent=2))
        else:
            print(list_all_patterns_markdown())
        return

    try:
        ind_key = resolve_pattern(args.industry, INDUSTRY_PATTERNS, "it-saas-web")
        role_key = resolve_pattern(args.role, ROLE_PATTERNS, "sales-cs")
        stage_key = resolve_pattern(args.stage, STAGE_PATTERNS, "first-interview")
        cand_key = resolve_pattern(args.candidate, CANDIDATE_PATTERNS, "new-grad")
        arch_key = resolve_pattern(args.archetype, ARCHETYPE_PATTERNS, "listed-enterprise")
    except ValueError as exc:
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

    if args.format == "json":
        print(json.dumps(bp, ensure_ascii=False, indent=2))
    else:
        print(format_blueprint_markdown(bp))


if __name__ == "__main__":
    main()
