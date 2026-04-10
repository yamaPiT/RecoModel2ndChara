"""
マルチエージェント再構成エンジン

このモジュールは、生成（Generator）と校正（Reviewer）の2段階のLLM処理を制御し、
ASDoQ品質モデルを最終的な高品質データへと再構築するパイプラインを管理します。

作成者: HAL (AI Agent)
作成日: 2026-04-10
"""

import os
from .llm_client import LLMClient

class Reconstructor:
    """
    Generator(生成) と Reviewer(校正) のマルチエージェントプロセスを管理するクラス。
    
    Attributes:
        llm_client (LLMClient): LLMとの通信を担当するクライアント。
        prompts_dir (str): プロンプトファイルが格納されているディレクトリ。
        prompt_generator (str): 第1フェーズ（生成）用のプロンプト本文。
        prompt_reviewer (str): 第2フェーズ（校正）用のプロンプト本文。
    """
    
    def __init__(self, prompts_dir: str):
        """
        Reconstructorクラスのコンストラクタ。
        
        Args:
            prompts_dir (str): プロンプトファイルが格納されているディレクトリ。
        """
        self.llm_client = LLMClient()
        self.prompts_dir = prompts_dir
        
        # プロンプトファイルのロード
        self.prompt_generator = self._load_prompt("prompt_01_generator.md")
        self.prompt_reviewer = self._load_prompt("prompt_02_reviewer.md")

    def _load_prompt(self, filename: str) -> str:
        """
        指定されたプロンプトファイルを読み込み、テキストとして返します。
        
        Args:
            filename (str): プロンプトファイル名。
            
        Returns:
            str: プロンプトのテキスト内容。
        """
        path = os.path.join(self.prompts_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def reconstruct(self, subchar_name: str, markdown_text: str) -> str:
        """
        1次処理（生成） -> 2次処理（校閲）のパイプラインを実行して、最終的なMarkdownテーブルを返します。
        
        各フェーズの中間結果はデバッグ用に logs/raw_ai_responses に保存されます。

        Args:
            subchar_name (str): 処理対象の副特性名。
            markdown_text (str): 抽出された元データのMarkdownテキスト。
            
        Returns:
            str: 二段階の処理を経て洗練された最終的なMarkdownテーブル。
        """
        # ログ出力用ディレクトリの準備
        log_dir = os.path.join(os.getcwd(), "logs", "raw_ai_responses")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # --- Phase 1: Generation (生成フェーズ) ---
        print(f"[{subchar_name}] Phase 1: Generating standard structure...")
        
        # プロンプト内のプレースホルダ {INPUT_MARKDOWN} を実データに置換
        gen_prompt = self.prompt_generator.replace("{INPUT_MARKDOWN}", markdown_text)
        
        # AI(Generator) によるテーブル構造の生成
        generated_table_raw = self.llm_client.generate_content(gen_prompt)
        
        # デバッグ用にフェーズ1の生回答を書き出し
        subchar_safe = subchar_name.replace("/", "_")
        with open(os.path.join(log_dir, f"{subchar_safe}_phase1_raw.md"), "w", encoding="utf-8") as f:
            f.write(generated_table_raw)
            
        # 余分なコードフェンス等を削除
        generated_table = self._clean_markdown_fences(generated_table_raw)
        
        # --- Phase 2: Review (校正フェーズ) ---
        print(f"[{subchar_name}] Phase 1 complete. Proceeding to Phase 2: Review...")
        
        # プロンプト内のプレースホルダ {INPUT_MARKDOWN_TABLE} をフェーズ1の結果に置換
        rev_prompt = self.prompt_reviewer.replace("{INPUT_MARKDOWN_TABLE}", generated_table)
        
        # AI(Reviewer) による品質校正・リライト
        reviewed_table_raw = self.llm_client.generate_content(rev_prompt)
        
        # デバッグ用にフェーズ2の生回答を書き出し
        with open(os.path.join(log_dir, f"{subchar_safe}_phase2_raw.md"), "w", encoding="utf-8") as f:
            f.write(reviewed_table_raw)

        # 最終的なクリーンアップ
        reviewed_table = self._clean_markdown_fences(reviewed_table_raw)
        
        print(f"[{subchar_name}] Phase 2 complete.")
        return reviewed_table

    def _clean_markdown_fences(self, text: str) -> str:
        """
        AI出力に含まれる Markdownコードフェンス (```) を除去するヘルパー。
        
        Args:
            text (str): 除去対象のテキスト。
            
        Returns:
            str: フェンスが除去されたクリーンなテキスト。
        """
        lines = text.strip().split("\n")
        # 文頭のフェンスを確認
        if lines and lines[0].startswith("```"):
            lines.pop(0)
        # 文末のフェンスを確認
        if lines and lines[-1].startswith("```"):
            lines.pop(-1)
        return "\n".join(lines).strip()
