"""
ASDoQ品質モデルデータ抽出モジュール

このモジュールは、ASDoQのMarkdownソースファイル（表形式）を解析し、
品質特性と副特性の階層関係を維持したまま、処理対象のテキストブロックを抽出します。

作成者: HAL (AI Agent)
作成日: 2026-04-10
"""

import os

class Extractor:
    """
    ASDoQ品質モデルのMarkdownファイルから、副特性ごとにデータを抽出するクラス。
    
    Attributes:
        file_path (str): 解析対象のMarkdownファイルへのパス。
    """
    
    def __init__(self, file_path: str):
        """
        Extractorクラスのコンストラクタ。
        
        Args:
            file_path (str): 解析対象のMarkdownファイルへのパス。
        """
        self.file_path = file_path

    def extract_subcharacteristics(self) -> dict:
        """
        Markdown内のテーブル形式を解析し、副特性名に紐づく行データの辞書を返します。
        
        Markdown中の品質特性（親）と品質副特性（子）のセル結合（空欄）を
        プログラム側で補完しながらパースします。

        Returns:
            dict: 副特性名をキーとし、親特性名と関連Markdownテキストを持つ辞書。
                例: {
                    "目的明示性": {"parent": "目的適合性", "markdown": "表のヘッダー + データ行"},
                    ...
                }
        """
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        extracted_data = {}
        current_parent_char = None
        current_subchar = None
        current_lines = []
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # 1. 抽出用ヘッダー情報の初期化
        header_found = False
        header_line = ""
        separator_line = ""
        
        # 2. Markdownファイルの全行走査
        for line in lines:
            line_stripped = line.strip()
            # テーブルの行以外（説明文等）はスキップ
            if not line_stripped.startswith('|'):
                continue
            
            # 2.1 テーブルヘッダーの特定
            if "品質特性" in line_stripped and "品質副特性" in line_stripped and not header_found:
                header_found = True
                header_line = line_stripped
                continue
                
            # 2.2 セパレーター行 (|---|---|...) の特定
            if header_found and set(line_stripped.replace('|', '').replace(':', '').replace('-', '').strip()) == set():
                separator_line = line_stripped
                continue
                
            # 2.3 データ行の処理
            if header_found:
                cols = [col.strip() for col in line_stripped.split('|')]
                
                # 有効なテーブル行かチェック (| 品質特性 | 分類 | 品質副特性 | ... |)
                # splitにより、両端の空文字を含めて 5要素以上あることを期待
                if len(cols) > 4:
                    parent_char_col = cols[1]  # 第1列: 品質特性 (Parent Characteristic)
                    subchar_col = cols[3]      # 第3列: 品質副特性 (Sub-characteristic)
                    
                    # 空欄の場合は直前の親特性を引き継ぐ（セル結合の補完）
                    new_parent_char = parent_char_col if parent_char_col else current_parent_char

                    if subchar_col:
                        # 新しい副特性の開始を検知
                        if current_subchar:
                            # これまでの累積データを保存
                            extracted_data[current_subchar] = {
                                "parent": current_parent_char,
                                "markdown": "\n".join([header_line, separator_line] + current_lines)
                            }
                        
                        # 状態の更新
                        current_parent_char = new_parent_char
                        current_subchar = subchar_col
                        current_lines = [line_stripped]
                    elif current_subchar:
                        # 副特性名が空欄の場合は、現在の副特性の継続行（測定項目が複数ある等）として扱う
                        current_lines.append(line_stripped)

        # 3. 最後に処理していたブロックを保存（ループ終了時の残データ処理）
        if current_subchar and current_lines:
            extracted_data[current_subchar] = {
                "parent": current_parent_char,
                "markdown": "\n".join([header_line, separator_line] + current_lines)
            }

        return extracted_data
