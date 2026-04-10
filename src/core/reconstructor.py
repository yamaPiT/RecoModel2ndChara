import os
from .llm_client import LLMClient

class Reconstructor:
    """Generator(生成) と Reviewer(校正) のマルチエージェントプロセスを管理するクラス"""
    
    def __init__(self, prompts_dir: str):
        self.llm_client = LLMClient()
        self.prompts_dir = prompts_dir
        
        # プロンプトのロード
        self.prompt_generator = self._load_prompt("prompt_01_generator.md")
        self.prompt_reviewer = self._load_prompt("prompt_02_reviewer.md")

    def _load_prompt(self, filename: str) -> str:
        path = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def reconstruct(self, subchar_name: str, markdown_text: str) -> str:
        """
        1次処理（生成） -> 2次処理（校閲）のパイプラインを実行して、最終的なMarkdownテーブルを返す。
        """
        # ログ出力用ディレクトリの準備
        log_dir = os.path.join(os.getcwd(), "logs", "raw_ai_responses")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        print(f"[{subchar_name}] Phase 1: Generating standard structure...")
        
        # 1次プロンプトのプレースホルダを置換 (プロンプト内のタグ {INPUT_MARKDOWN} に合わせる)
        gen_prompt = self.prompt_generator.replace("{INPUT_MARKDOWN}", markdown_text)
        
        # Generator による生成
        generated_table_raw = self.llm_client.generate_content(gen_prompt)
        
        # デバッグ用に生回答を保存
        subchar_safe = subchar_name.replace("/", "_")
        with open(os.path.join(log_dir, f"{subchar_safe}_phase1_raw.md"), "w", encoding="utf-8") as f:
            f.write(generated_table_raw)
            
        generated_table = self._clean_markdown_fences(generated_table_raw)
        
        print(f"[{subchar_name}] Phase 1 complete. Proceeding to Phase 2: Review...")
        
        # 2次プロンプトのプレースホルダを置換
        rev_prompt = self.prompt_reviewer.replace("{INPUT_MARKDOWN_TABLE}", generated_table)
        
        # Reviewer による校閲
        reviewed_table_raw = self.llm_client.generate_content(rev_prompt)
        
        with open(os.path.join(log_dir, f"{subchar_safe}_phase2_raw.md"), "w", encoding="utf-8") as f:
            f.write(reviewed_table_raw)

        reviewed_table = self._clean_markdown_fences(reviewed_table_raw)
        
        print(f"[{subchar_name}] Phase 2 complete.")
        return reviewed_table

    def _clean_markdown_fences(self, text: str) -> str:
        """出力から ``` や ```markdown 等のコードフェンスを除去するヘルパー"""
        lines = text.strip().split("\n")
        if lines and lines[0].startswith("```"):
            lines.pop(0)
        if lines and lines[-1].startswith("```"):
            lines.pop(-1)
        return "\n".join(lines).strip()
