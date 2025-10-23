"""
改良版API料金計算モジュール
LangChainのcallbackと手動計算を組み合わせた統合ソリューション
"""

import tiktoken
import requests
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from contextlib import contextmanager
from langchain_openai import OpenAI
from langchain_community.callbacks import get_openai_callback
import logging

class EnhancedCostCalculator:
    def __init__(self):
        """改良版料金計算器の初期化"""
        # OpenAI API料金（2024年12月時点、USD/1000トークン）
        self.pricing = {
            "gpt-4o-mini": {
                "input": 0.00015,   # $0.15 per 1M tokens
                "output": 0.0006    # $0.60 per 1M tokens
            },
            "gpt-4o": {
                "input": 0.005,     # $5.00 per 1M tokens
                "output": 0.015     # $15.00 per 1M tokens
            },
            "text-embedding-3-small": {
                "input": 0.00002,   # $0.02 per 1M tokens
                "output": 0.0       # 埋め込みは出力なし
            },
            "text-embedding-3-large": {
                "input": 0.00013,   # $0.13 per 1M tokens
                "output": 0.0       # 埋め込みは出力なし
            }
        }
        
        # 為替レート（USD/JPY）
        self.exchange_rate = self._get_exchange_rate()
        
        # セッション統計（シンプル版）
        self.session_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_cost_jpy": 0.0
        }
        
    def _get_exchange_rate(self) -> float:
        """為替レートを取得（USD/JPY）"""
        try:
            response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=5)
            data = response.json()
            return data["rates"]["JPY"]
        except Exception as e:
            logging.warning(f"為替レート取得エラー: {e}")
            return 150.0
    
    def count_tokens(self, text: str, model: str = "gpt-4o-mini") -> int:
        """テキストのトークン数を計算"""
        try:
            if model.startswith("gpt-4o"):
                encoding = tiktoken.get_encoding("o200k_base")
            elif model.startswith("text-embedding"):
                encoding = tiktoken.get_encoding("cl100k_base")
            else:
                encoding = tiktoken.get_encoding("cl100k_base")
            
            return len(encoding.encode(text))
        except Exception as e:
            logging.warning(f"トークン計算エラー: {e}")
            return int(len(text) * 0.25)
    
    def calculate_cost(self, input_text: str, output_text: str = "", model: str = "gpt-4o-mini") -> Dict[str, float]:
        """API使用料金を計算"""
        # トークン数の計算
        input_tokens = self.count_tokens(input_text, model)
        output_tokens = self.count_tokens(output_text, model) if output_text else 0
        
        # モデルの料金設定を取得
        if model not in self.pricing:
            logging.warning(f"モデル {model} の料金設定が見つかりません。gpt-4o-miniの料金を使用します。")
            model = "gpt-4o-mini"
        
        pricing = self.pricing[model]
        
        # USDでの料金計算
        input_cost_usd = (input_tokens / 1000) * pricing["input"]
        output_cost_usd = (output_tokens / 1000) * pricing["output"]
        total_cost_usd = input_cost_usd + output_cost_usd
        
        # JPYでの料金計算
        total_cost_jpy = total_cost_usd * self.exchange_rate
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost_usd": input_cost_usd,
            "output_cost_usd": output_cost_usd,
            "total_cost_usd": total_cost_usd,
            "total_cost_jpy": total_cost_jpy,
            "exchange_rate": self.exchange_rate,
            "model": model
        }
    
    @contextmanager
    def track_cost(self, model: str = "gpt-4o-mini", operation_name: str = "API呼び出し"):
        """コスト追跡コンテキストマネージャー"""
        start_time = datetime.now()
        
        with get_openai_callback() as callback:
            try:
                yield callback
                
                # コールバックから取得した情報
                callback_data = {
                    "prompt_tokens": callback.prompt_tokens,
                    "completion_tokens": callback.completion_tokens,
                    "total_tokens": callback.total_tokens,
                    "total_cost_usd": callback.total_cost,
                    "model": model,
                    "operation_name": operation_name,
                    "start_time": start_time,
                    "end_time": datetime.now(),
                    "duration_seconds": (datetime.now() - start_time).total_seconds()
                }
                
                # JPYでの料金計算
                callback_data["total_cost_jpy"] = callback.total_cost * self.exchange_rate
                
                # セッション統計の更新
                self._update_session_stats(callback_data)
                
                # 詳細レポートの生成
                self._print_cost_report(callback_data)
                
            except Exception as e:
                logging.error(f"コスト追跡中にエラーが発生しました: {e}")
                raise
    
    def _update_session_stats(self, callback_data: Dict[str, Any]):
        """セッション統計を更新（シンプル版）"""
        self.session_stats["total_calls"] += 1
        self.session_stats["total_tokens"] += callback_data["total_tokens"]
        self.session_stats["total_cost_usd"] += callback_data["total_cost_usd"]
        self.session_stats["total_cost_jpy"] += callback_data["total_cost_jpy"]
    
    def _print_cost_report(self, callback_data: Dict[str, Any]):
        """コストレポートを出力"""
        print(f"\n💰 {callback_data['operation_name']} - 料金レポート")
        print(f"モデル: {callback_data['model']}")
        print(f"入力トークン数: {callback_data['prompt_tokens']:,}")
        print(f"出力トークン数: {callback_data['completion_tokens']:,}")
        print(f"合計トークン数: {callback_data['total_tokens']:,}")
        print(f"処理時間: {callback_data['duration_seconds']:.2f}秒")
        print(f"料金（USD）: ${callback_data['total_cost_usd']:.6f}")
        print(f"料金（JPY）: ¥{callback_data['total_cost_jpy']:.2f}")
        print("-" * 50)
    
    def generate_llm_response_with_cost_tracking(self, chain_type: str, llm, retriever, query: str, operation_name: str = "RAG検索"):
        """改良版LLM応答生成（コスト追跡付き）"""
        from langchain_community.chains import RetrievalQA
        
        chain = RetrievalQA.from_chain_type(
            llm=llm, 
            chain_type=chain_type, 
            retriever=retriever
        )
        
        with self.track_cost(llm.model_name, operation_name) as callback:
            result = chain.run(query)
            
            # 追加の詳細情報
            print(f"🔍 検索クエリ: {query[:50]}...")
            print(f"📊 レスポンス長: {len(result)}文字")
            
            return result
    
    def get_session_summary(self) -> Dict[str, Any]:
        """セッション統計のサマリーを取得"""
        return {
            "session_stats": self.session_stats.copy(),
            "exchange_rate": self.exchange_rate,
            "summary_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def print_session_summary(self):
        """セッション統計を出力（シンプル版）"""
        stats = self.session_stats
        
        print("\n" + "="*50)
        print("📈 セッション統計サマリー")
        print("="*50)
        print(f"総API呼び出し回数: {stats['total_calls']:,}")
        print(f"総トークン数: {stats['total_tokens']:,}")
        print(f"総料金（JPY）: ¥{stats['total_cost_jpy']:.2f}")
        print("="*50)
    
    def reset_session_stats(self):
        """セッション統計をリセット（シンプル版）"""
        self.session_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_cost_jpy": 0.0
        }
        print("🔄 セッション統計をリセットしました。")

# グローバルインスタンス
enhanced_calculator = EnhancedCostCalculator()

def generate_llm_response_with_tracking(chain_type: str, llm, retriever, query: str, operation_name: str = "RAG検索"):
    """改良版LLM応答生成関数"""
    return enhanced_calculator.generate_llm_response_with_cost_tracking(
        chain_type, llm, retriever, query, operation_name
    )

def get_session_summary():
    """セッション統計を取得"""
    return enhanced_calculator.get_session_summary()

def print_session_summary():
    """セッション統計を出力"""
    enhanced_calculator.print_session_summary()

def reset_session_stats():
    """セッション統計をリセット"""
    enhanced_calculator.reset_session_stats()
