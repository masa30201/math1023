"""
数学問題類題作成ツール（シンプル版）
問題検索機能を削除し、類題生成機能のみに特化
"""

import os
import warnings
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from enhanced_cost_calculator import (
    enhanced_calculator,
    print_session_summary,
    reset_session_stats
)

# Pydanticの警告を非表示にする
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

class SimpleMathProblemGenerator:
    def __init__(self, api_key: str):
        """
        シンプル版数学問題生成器の初期化
        
        Args:
            api_key: OpenAI APIキー
        """
        # OpenAI APIキーの設定
        os.environ["OPENAI_API_KEY"] = api_key
        
        # LLMの設定
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    def _parse_multiple_choice_problem(self, problem_text: str) -> Dict[str, Any]:
        """多肢選択問題を構造化して解析"""
        import re
        
        # 比率問題のパターンを検出
        ratio_pattern = r'(\d+)人は(\d+)人の([0-9.]+)にあたります'
        ratio_match = re.search(ratio_pattern, problem_text)
        
        if ratio_match:
            compared_value = ratio_match.group(1) + "人"
            base_value = ratio_match.group(2) + "人"
            ratio = ratio_match.group(3)
            
            # 選択肢を抽出
            choices_pattern = r'もとにする量：([^くらべられる量]+)くらべられる量：(.+)'
            choices_match = re.search(choices_pattern, problem_text)
            
            if choices_match:
                base_choices = [choice.strip() for choice in choices_match.group(1).split('/')]
                compared_choices = [choice.strip() for choice in choices_match.group(2).split('/')]
                
                return {
                    "type": "ratio_multiple_choice",
                    "question": ratio_match.group(0),
                    "compared_value": compared_value,
                    "base_value": base_value,
                    "ratio": ratio,
                    "base_choices": base_choices,
                    "compared_choices": compared_choices,
                    "correct_answer": {
                        "base": base_value,
                        "compared": compared_value
                    }
                }
        
        return {
            "type": "general_multiple_choice",
            "question": problem_text,
            "choices": [],
            "correct_answer": None
        }
        
    def generate_similar_problem(self, original_problem: str, difficulty_level: str = "中級") -> Dict[str, Any]:
        """類題の生成"""
        # 多肢選択問題かどうかを判定
        is_multiple_choice = any(keyword in original_problem for keyword in ["選択肢", "ア", "イ", "ウ", "エ", "A", "B", "C", "D", "/", "もとにする量", "くらべられる量"])
        
        if is_multiple_choice:
            # 選択肢を構造化して解析
            structured_problem = self._parse_multiple_choice_problem(original_problem)
            
            if structured_problem["type"] == "ratio_multiple_choice":
                # 比率問題用の構造化プロンプト
                prompt = f"""
                以下の中学数学問題を参考にして、{difficulty_level}レベルの多肢選択類題を作成してください。
                
                【元の問題の構造化情報】
                問題文: {structured_problem["question"]}
                もとにする量の選択肢: {structured_problem["base_choices"]}
                くらべられる量の選択肢: {structured_problem["compared_choices"]}
                正解: もとにする量={structured_problem["correct_answer"]["base"]}, くらべられる量={structured_problem["correct_answer"]["compared"]}
                
                【類題作成指示】
                以下の形式で回答してください：
                1. 類題の問題文（選択肢を含む）
                2. 正解（選択肢の記号のみ）
                3. 解説（なぜその選択肢が正解なのか）
                4. 使用した数学的概念
                
                【重要】
                - 数値は適切に変更してください（例：64→45、80→60、0.8→0.75など）
                - 選択肢の構造は元の問題と同じにしてください
                - もとにする量の選択肢とくらべられる量の選択肢を明確に分けて提示してください
                - 各選択肢は「ア」「イ」「ウ」「エ」で区別してください
                - 正解は選択肢の記号のみで答えてください
                """
            else:
                # 一般的な多肢選択問題用のプロンプト
                prompt = f"""
                以下の中学数学問題を参考にして、{difficulty_level}レベルの多肢選択類題を作成してください。
                
                元の問題: {original_problem}
                
                以下の形式で回答してください：
                1. 類題の問題文（選択肢を含む）
                2. 正解（選択肢の記号のみ）
                3. 解説（なぜその選択肢が正解なのか）
                4. 使用した数学的概念
                
                重要：
                - 選択肢は問題文に含めてください
                - 解答では選択肢の記号（ア、イ、ウ、エなど）のみを答えてください
                - 選択肢の内容は適切に変更し、同じ解法パターンを使う類題を作成してください
                - 数値は適切に変更してください
                """
        else:
            # 通常の問題用のプロンプト
            prompt = f"""
            以下の中学数学問題を参考にして、{difficulty_level}レベルの類題を作成してください。
            
            元の問題: {original_problem}
            
            以下の形式で回答してください：
            1. 類題の問題文
            2. 解答
            3. 解説
            4. 使用した数学的概念
            
            数値は適切に変更し、同じ解法パターンを使う類題を作成してください。
            計算が必要な場合は、正確な数値を計算して示してください。
            """
        
        try:
            # 改良版のコスト追跡を使用
            with enhanced_calculator.track_cost("gpt-4o-mini", f"類題生成({difficulty_level})") as callback:
                response = self.llm.invoke(prompt)
                
                # 結果を構造化
                generated_problem = {
                    "original_problem": original_problem,
                    "difficulty_level": difficulty_level,
                    "generated_content": response.content,
                    "generation_prompt": prompt,
                    "cost_data": {
                        "prompt_tokens": callback.prompt_tokens,
                        "completion_tokens": callback.completion_tokens,
                        "total_tokens": callback.total_tokens,
                        "total_cost_usd": callback.total_cost,
                        "total_cost_jpy": callback.total_cost * enhanced_calculator.exchange_rate,
                        "model": "gpt-4o-mini"
                    }
                }
                
                return generated_problem
                
        except Exception as e:
            print(f"類題生成中にエラーが発生しました: {e}")
            return {"error": str(e)}
    
    def generate_multiple_problems(self, original_problem: str, difficulties: list = ["初級", "中級", "上級"]) -> Dict[str, Any]:
        """複数の難易度で類題を生成"""
        results = {}
        total_cost = 0.0
        
        print(f"📚 複数難易度での類題生成を開始...")
        print(f"元の問題: {original_problem}")
        print("="*60)
        
        for difficulty in difficulties:
            print(f"\n🎯 難易度: {difficulty}")
            result = self.generate_similar_problem(original_problem, difficulty)
            
            if "error" not in result:
                results[difficulty] = result
                if "cost_data" in result:
                    total_cost += result["cost_data"]["total_cost_jpy"]
                print(f"✅ {difficulty}レベルの類題を生成しました")
            else:
                print(f"❌ {difficulty}レベルの生成に失敗: {result['error']}")
        
        print("\n" + "="*60)
        print(f"📊 生成完了 - 総料金: ¥{total_cost:.4f}")
        
        return {
            "results": results,
            "total_cost_jpy": total_cost,
            "difficulties": difficulties
        }
    
    def get_session_summary(self):
        """セッション統計を取得"""
        return enhanced_calculator.get_session_summary()
    
    def print_session_summary(self):
        """セッション統計を出力"""
        enhanced_calculator.print_session_summary()
    
    def reset_session_stats(self):
        """セッション統計をリセット"""
        enhanced_calculator.reset_session_stats()

def main():
    """メイン実行関数"""
    # APIキーの設定（実際の使用時は環境変数から取得）
    api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
    
    if api_key == "your-openai-api-key-here":
        print("⚠️  OpenAI APIキーを設定してください。")
        print("環境変数 OPENAI_API_KEY を設定するか、.envファイルで設定してください。")
        return
    
    # シンプル版数学問題生成器の初期化
    generator = SimpleMathProblemGenerator(api_key)
    
    # セッション統計をリセット
    generator.reset_session_stats()
    
    # 実際の使用例
    print("🎓 数学問題類題作成ツール（シンプル版）")
    print("="*50)
    
    # 複数難易度での類題生成例
    sample_problem = "x + 5 = 12 を解きなさい。"
    print(f"元の問題: {sample_problem}")
    
    results = generator.generate_multiple_problems(sample_problem, ["初級", "中級", "上級"])
    
    # 生成された類題の表示
    print("\n📝 生成された類題:")
    for difficulty, result in results["results"].items():
        print(f"\n【{difficulty}レベル】")
        print("-" * 50)
        print(result["generated_content"])
        print("-" * 50)
    
    # セッション統計の表示
    print("\n📊 セッション統計:")
    generator.print_session_summary()

if __name__ == "__main__":
    main()
