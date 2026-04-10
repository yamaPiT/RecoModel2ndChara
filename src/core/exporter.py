import os
import openpyxl
from openpyxl.styles import Alignment, Font

class Exporter:
    """最終的なMarkdownテーブルをパースし、Excelファイルとして出力するクラス"""

    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def export_to_excel(self, parent_char: str, subchar: str, markdown_table: str, author_prefix="(山本)"):
        """
        Markdownテーブルを解析し、エクセルに出力する。
        ファイル名例: (山本)保守性_持続可能性_再構成.xlsx
        """
        parent_prefix = f"{parent_char}_" if parent_char else ""
        
        # 安全なファイル名の生成
        safe_subchar = subchar.replace("/", "_").replace("\\", "_")
        safe_parent = parent_prefix.replace("/", "_")
        
        # 望ましいファイル名: (山本)品質特性_品質副特性_再構成.xlsx
        filename = f"{author_prefix}{safe_parent}{safe_subchar}_再構成.xlsx"
        filepath = os.path.join(self.output_dir, filename)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = safe_subchar[:31]  # シート名は31文字制限

        # (山本) 1行目に固定ヘッダーを書き込む
        headers = ["測定項目", "測定基準", "記述例（適合例／非適合例）"]
        for col_idx, header_text in enumerate(headers, start=1):
            ws.cell(row=1, column=col_idx, value=header_text)

        lines = markdown_table.strip().split("\n")
        
        row_idx = 2 # データは2行目から書き込む
        table_started = False
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Markdownテーブルの行を抽出 ("| A | B | C |")
            if line.startswith("|") and line.endswith("|"):
                # セパレータ行 (例: |---|:---|) を検知してスキップ
                # - が複数並んでいるか、: が含まれている行はセパレータとみなす
                content_only = line[1:-1].replace(" ", "").replace("|", "")
                if all(c in "-:" for c in content_only) and len(content_only) > 0:
                    continue
                
                # ヘッダー行 (測定項目, 測定基準, 記述例) もスキップ (1行目はプログラム側で制御するため)
                if "測定項目" in line and "測定基準" in line:
                    table_started = True # ヘッダーを見つけたらテーブル開始とみなす
                    continue
                
                # テーブル開始前（説明文など）の | 行は無視する
                if not table_started:
                    # 指示書に「出力形式」としてテーブルの例が含まれている場合があるため、
                    # 最初のデータ行っぽく見えるものを見つけるまでは慎重に扱う
                    # ただし、ASDoQの測定項目は「文書」や「記述」などで始まることが多いため、ある程度推測可能
                    pass

                # 両端の | を削除してからスプリット
                cols = [c.strip() for c in line[1:-1].split("|")]
                # 最低3列あることを期待
                if len(cols) < 3:
                    continue
                
                # 必要な3列のみを処理
                target_cols = cols[:3]
                
                for col_idx, col_val in enumerate(target_cols, start=1):
                    # セル内の 【改行】 プレースホルダを実際の改行(\n)に変換
                    cell_value = col_val.replace("【改行】", "\n")
                    cell = ws.cell(row=row_idx, column=col_idx, value=cell_value)
                row_idx += 1

        # 書式設定（JTFや提供されたサンプルに準拠）
        font_header = Font(name="メイリオ", size=10, bold=True)
        font_data = Font(name="メイリオ", size=10, bold=False)
        align_header = Alignment(horizontal="center", vertical="center", wrap_text=True)
        align_data = Alignment(horizontal="left", vertical="top", wrap_text=True)

        for row_idx_curr, row in enumerate(ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=3), start=1):
            is_header = (row_idx_curr == 1)
            for cell in row:
                cell.font = font_header if is_header else font_data
                cell.alignment = align_header if is_header else align_data

        # 列幅の固定（サンプルのExcelの仕様）
        ws.column_dimensions['A'].width = 26.13
        ws.column_dimensions['B'].width = 44.38
        ws.column_dimensions['C'].width = 110.0

        wb.save(filepath)
        print(f"Exported Excel to: {filepath}")
        return filepath
