"""
LLM API クライアントモジュール

このモジュールは、Google Gemini API との通信を仲介します。
指数バックオフによるリトライ処理を実装し、安定したコンテンツ生成を提供します。

作成者: HAL (AI Agent)
作成日: 2026-04-10
"""

import os
import time
from google import genai
from dotenv import load_dotenv

# 環境変数の読み込み (.env ファイルから API キーをロード)
load_dotenv()

class LLMClient:
    """
    Gemini API との通信を担当するクライアントクラス。
    
    Attributes:
        api_key (str): Gemini APIを利用するための認証キー。
        client (genai.Client): Google GenAI SDKのクライアントインスタンス。
        model_name (str): 使用するLLMモデルの名称。
    """
    
    def __init__(self):
        """
        LLMClientクラスのコンストラクタ。
        環境変数からAPIキーを取得し、Google GenAIクライアントを初期化します。
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set.")
        
        # google-genai のクライアント初期化
        self.client = genai.Client(api_key=self.api_key)
        
        # モデルの指定 (Gemini 2.0 Flash / 3.1 Pro 相当の最新プレビュー版を使用)
        self.model_name = "gemini-3-flash-preview"
        
    def generate_content(self, prompt: str, max_retries=3, backoff_factor=2) -> str:
        """
        指定されたプロンプトに対する応答テキストを生成します。
        
        ネットワークエラーやレート制限に備え、指数バックオフアルゴリズムによる
        自動リトライ処理を行います。

        Args:
            prompt (str): AIに送信するプロンプト全文。
            max_retries (int): 失敗時の最大リトライ回数。デフォルトは3回。
            backoff_factor (int): 指数バックオフの係数。

        Returns:
            str: AIから返却された生成テキスト。

        Raises:
            Exception: 最大リトライ回数を超えても成功しなかった場合に発生。
        """
        for attempt in range(max_retries):
            try:
                # モデル経由でコンテンツ生成リクエストを送信
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                )
                if response and response.text:
                    return response.text
                return ""
            except Exception as e:
                # 失敗時はログを出力し、待機後にリトライ
                print(f"LLM API Error (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    # 指数バックオフによる待機時間の計算 (1s, 2s, 4s...)
                    sleep_time = backoff_factor ** attempt
                    time.sleep(sleep_time)
                else:
                    # 全てのリトライが失敗した場合は呼び出し元へ例外を伝播
                    raise Exception(f"Failed to generate content after {max_retries} attempts.") from e
