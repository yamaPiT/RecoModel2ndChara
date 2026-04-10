import os
import time
from google import genai
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """Gemini API との通信を担当するクライアントクラス"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
        # google-genai のクライアント初期化
        self.client = genai.Client(api_key=self.api_key)
        # Gemini 3 Flash Preview を使用
        self.model_name = "gemini-3-flash-preview"
        
    def generate_content(self, prompt: str, max_retries=3, backoff_factor=2) -> str:
        """
        プロンプトに対する応答を生成する。
        API制限等への対応としてリトライ処理を組み込む。
        """
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
                return ""
            except Exception as e:
                print(f"LLM API Error (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                else:
                    raise Exception(f"Failed to generate content after {max_retries} attempts.") from e
