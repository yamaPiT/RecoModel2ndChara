# ASDoQ 品質モデル再構成ツール (RecoModel2ndChara) 🤖📊

本リポジトリは、ASDoQ（システム開発文書品質研究会）が定義する「文書品質モデル v2.0a-3」の全17個の品質副特性を、最新のLLM（Gemini API）を用いて高品質な実務用Excelファイルへと自動的に再構成するマルチエージェント・システムです。

---

## 🌟 主な特徴

- **マルチエージェント・パイプライン**: 生成（Generator）と校正（Reviewer）の2段階処理により、極めて高い生成精度を実現。
- **実務に即使える品質**: 
    - **JTF日本語標準スタイルガイド**および**公用文作成ルール**に完全準拠。
    - 測定項目を単に言い換えるのではなく、実務的な「判定の尺度」としての情報をAI自ら付加。
- **高品質なExcel出力**:
    - **メイリオ・フォント**を全セルに適用した美しいレイアウト。
    - 1行目に正式ヘッダーを固定し、セル内改行（Alt+Enter）も自動処理。
- **DADAプロセス準拠**: ドキュメントを軸としたアジャイル開発手法「DADA」に基づき構築。

---

## 📖 開発プロセス (DADA)

本システムは、**DADA（Document-and-Agent-Driven Agile）** プロセスに従って開発されました。これは、AIエージェントが「要求仕様書」や「設計書」を自律的に最新へと更新し、人間（Product Owner）がそれを承認してから実装・テストに進む手法です。

### DADAプロセス フローチャート
```mermaid
graph TD
    Start(["開始"]) --> UserReq["人間からの要求アイデア"]
    UserReq --> Req["要求定義工程 - Requirements Engineer"]
    Req --> ReqRev["自己レビュー - Self-Correction"]
    ReqRev --> ReqHum["🔴 人間による承認"]
    ReqHum -- 承認 --> Arch["アーキテクチャ設計工程 - Architect"]
    Arch --> ArchRev["自己レビュー - Self-Correction"]
    ArchRev --> ArchHum["🔴 人間による承認"]
    ArchHum -- 承認 --> Impl["自律的実装・詳細テスト - Programmer"]
    Impl --> ImplLoop["エラー自己修復ループ - 自動デバッグ"]
    ImplLoop -- オールグリーン --> Test["総合テスト仕様・報告書作成"]
    Test --> TestRev["自己レビュー - トレーサビリティ確認"]
    TestRev --> Approve["🔴 人間による最終評価"]
    Approve -- 完了 --> End(["終了"])

    %% ドキュメント（データストア）の紐付け
    Req -.-> ReqDoc[("SW105 ソフトウェア要求仕様書")]
    Arch -.-> ArchDoc[("SW205 アーキテクチャ設計書")]
    Test -.-> TestDoc[("SWP6 ソフトウェア総合テスト仕様書")]

    classDef human fill:#333333,stroke:#ff0000,stroke-width:2px,color:#ffffff;
    classDef agent fill:#333333,stroke:#FFFFFF,stroke-width:1px,color:#ffffff;
    classDef doc fill:#333333,stroke:#2e7d32,stroke-width:2px,color:#ffffff;
    class UserReq,ReqHum,ArchHum,Approve human;
    class Req,ReqRev,Arch,ArchRev,Impl,ImplLoop,Test,TestRev agent;
    class ReqDoc,ArchDoc,TestDoc doc;
```

---

## 🚀 クイックスタート

### 1. 準備
1.  Python 3.10 以上がインストールされていることを確認します。
2.  依存パッケージをインストールします：
    ```bash
    pip install -r requirements.txt
    ```
3.  `.env.example` をコピーして `.env` を作成し、Google Gemini APIキーを設定します：
    ```env
    GEMINI_API_KEY=あなたのAPIキー
    ```

### 2. 実行
メインスクリプトを実行すると、全17副特性の再構成が開始されます。
```bash
python src/main.py
```

*   **テストモード**: 最初の2項目のみ実行する場合は `--test` フラグを付けます。
*   **個別実行**: 特定の副特性のみ実行する場合は `--subchar [副特性名]` を指定します。

---

## 📁 ディレクトリ構成

- `src/`: プログラミングソースコード（Extractor, Reconstructor, Exporter）
- `doc/`: 開発ドキュメント（要求仕様書、設計書、テスト報告書）
- `doc/prompts/`: AIエージェントへの最新指示プロンプト
- `output/`: 生成されたExcelファイル（.xlsx）の出力先
- `logs/`: 生成プロセスにおけるAIの生回答ログ

---

## ⚖️ ライセンス / 免責事項
本ツールの出力結果はAIによる生成物です。最終的な品質判断や適用は、必ず人間（実務担当者）の責任において行ってください。

---

> [!NOTE]
> 本リポジトリは、Google Antigravity と DADAプロセスの力を最大限に引き出して構築されました。