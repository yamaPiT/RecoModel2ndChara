import os

class Extractor:
    """ASDoQ品質モデルのMarkdownファイルから、副特性ごとにデータを抽出するクラス"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path

    def extract_subcharacteristics(self) -> dict:
        """
        Markdownテーブルを解析し、副特性名に紐づく行データの辞書を返す。
        戻り値: {
            "目的明示性": {"parent": "目的適合性", "markdown": "抽出された関連Markdownテキスト"},
            "目的合致性": {"parent": "目的適合性", "markdown": "抽出された関連Markdownテキスト"},
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
            
        # ヘッダーを探す
        header_found = False
        header_line = ""
        separator_line = ""
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped.startswith('|'):
                continue
                
            if "品質特性" in line_stripped and "品質副特性" in line_stripped and not header_found:
                header_found = True
                header_line = line_stripped
                continue
                
            if header_found and set(line_stripped.replace('|', '').replace(':', '').replace('-', '').strip()) == set():
                # セパレーター行 (|---|---|...)
                separator_line = line_stripped
                continue
                
            if header_found:
                cols = [col.strip() for col in line_stripped.split('|')]
                
                # columns length check: | a | b | c | -> split gives ['', 'a', 'b', 'c', '']
                if len(cols) > 4:
                    parent_char_col = cols[1]  # インデックス1(品質特性)
                    subchar_col = cols[3]      # インデックス3(品質副特性)
                    
                    new_parent_char = parent_char_col if parent_char_col else current_parent_char

                    if subchar_col:
                        # 新しい副特性の開始
                        if current_subchar:
                            # 既存のものを保存
                            extracted_data[current_subchar] = {
                                "parent": current_parent_char,
                                "markdown": "\n".join([header_line, separator_line] + current_lines)
                            }
                        
                        current_parent_char = new_parent_char
                        current_subchar = subchar_col
                        current_lines = [line_stripped]
                    elif current_subchar:
                        # 副特性名が空欄の場合は継続行
                        current_lines.append(line_stripped)

        # 最後のブロックを保存
        if current_subchar and current_lines:
            extracted_data[current_subchar] = {
                "parent": current_parent_char,
                "markdown": "\n".join([header_line, separator_line] + current_lines)
            }

        return extracted_data
