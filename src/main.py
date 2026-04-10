"""
ASDoQ品質モデル再構成パイプライン - メインエントリポイント

このモジュールは、Markdown形式のASDoQ品質モデルファイルを読み込み、
マルチエージェントプロセス（抽出・再構成・出力）を制御する実行基盤です。

作成者: HAL (AI Agent)
作成日: 2026-04-10
"""

import os
import argparse
from core.extractor import Extractor
from core.reconstructor import Reconstructor
from core.exporter import Exporter

def main():
    """
    プログラムのメイン実行処理。
    引数解析、プロジェクトルートの特定、および各フェーズの実行を制御します。
    """
    # 1. 実行時引数の解析
    parser = argparse.ArgumentParser(description="ASDoQ Quality Model Reconstructor Pipeline")
    parser.add_argument("--test", action="store_true", help="1〜2個の副特性のみテスト実行する")
    parser.add_argument("--subchar", type=str, help="特定の副特性のみ実行する（例: 持続可能性）")
    args = parser.parse_args()

    # 2. パス構成の初期化（自身のファイル位置を基準にプロジェクトルートを特定）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_md = os.path.join(project_root, "doc", "参考資料", "ASDoQ_SystemDocumentationQualityModel_v2.0a-3.md")
    prompts_dir = os.path.join(project_root, "doc", "prompts")
    output_dir = os.path.join(project_root, "output")

    # 3. データの抽出フェーズ (Extraction Phase)
    # 元のMarkdownファイルから品質特性・副特性の階層を維持したまま、処理対象を抽出します。
    print("Extracting data from Markdown...")
    extractor = Extractor(target_md)
    extracted_data = extractor.extract_subcharacteristics()
    print(f"Extracted {len(extracted_data)} sub-characteristics.")

    # 4. 実行対象のフィルタリング
    # --subchar 指定や --test モードに基づき、ループを回すサブチャラ特性を特定します。
    target_keys = list(extracted_data.keys())
    if args.subchar:
        if args.subchar in target_keys:
            target_keys = [args.subchar]
        else:
            print(f"Error: Sub-characteristic '{args.subchar}' not found.")
            return
    elif args.test:
        target_keys = target_keys[:2]  # テストモードは最初の2つのみを実行対象とする
        print(f"Test mode: processing {target_keys}")

    # 5. コンポーネントの初期化
    reconstructor = Reconstructor(prompts_dir)
    exporter = Exporter(output_dir)

    # 6. パイプライン実行（生成 -> 校閲 -> 出力）
    # 各副特性に対して独立した再構成プロセスを回します。
    for subchar in target_keys:
        data = extracted_data[subchar]
        parent_char = data["parent"]
        markdown_text = data["markdown"]
        
        print(f"\n--- Processing: 【{parent_char}】 - {subchar} ---")
        try:
            # 6.1 LLMによる再構築プロセス（Phase 1: Generator -> Phase 2: Reviewer）
            final_markdown_table = reconstructor.reconstruct(subchar, markdown_text)
            
            # 6.2 最終結果をExcelファイルとして保存
            exporter.export_to_excel(parent_char, subchar, final_markdown_table)
            
            print(f"Successfully processed {subchar}.")
        except Exception as e:
            # 1つの処理失敗でも全体の停止を避けるため、例外をキャッチして次へ進む
            print(f"Failed to process {subchar}. Error: {e}")

if __name__ == "__main__":
    main()
