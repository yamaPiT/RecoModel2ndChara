import os
import argparse
from core.extractor import Extractor
from core.reconstructor import Reconstructor
from core.exporter import Exporter

def main():
    parser = argparse.ArgumentParser(description="ASDoQ Quality Model Reconstructor Pipeline")
    parser.add_argument("--test", action="store_true", help="1〜2個の副特性のみテスト実行する")
    parser.add_argument("--subchar", type=str, help="特定の副特性のみ実行する（例: 持続可能性）")
    args = parser.parse_args()

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_md = os.path.join(project_root, "doc", "参考資料", "ASDoQ_SystemDocumentationQualityModel_v2.0a-3.md")
    prompts_dir = os.path.join(project_root, "doc", "prompts")
    output_dir = os.path.join(project_root, "output")

    # 1. データの抽出
    print("Extracting data from Markdown...")
    extractor = Extractor(target_md)
    extracted_data = extractor.extract_subcharacteristics()
    print(f"Extracted {len(extracted_data)} sub-characteristics.")

    # 2. 対象の絞り込み
    target_keys = list(extracted_data.keys())
    if args.subchar:
        if args.subchar in target_keys:
            target_keys = [args.subchar]
        else:
            print(f"Error: Sub-characteristic '{args.subchar}' not found.")
            return
    elif args.test:
        target_keys = target_keys[:2]  # テストモードは最初の2つだけ
        print(f"Test mode: processing {target_keys}")

    # パイプラインコンポーネントの初期化
    reconstructor = Reconstructor(prompts_dir)
    exporter = Exporter(output_dir)

    # 3. パイプライン実行（生成 -> 校閲 -> 出力）
    for subchar in target_keys:
        data = extracted_data[subchar]
        parent_char = data["parent"]
        markdown_text = data["markdown"]
        
        print(f"\n--- Processing: 【{parent_char}】 - {subchar} ---")
        try:
            # 再構築（マルチエージェント処理）
            final_markdown_table = reconstructor.reconstruct(subchar, markdown_text)
            
            # Excelへ出力
            exporter.export_to_excel(parent_char, subchar, final_markdown_table)
            
            print(f"Successfully processed {subchar}.")
        except Exception as e:
            print(f"Failed to process {subchar}. Error: {e}")

if __name__ == "__main__":
    main()
