"""
プログラムでの直接使用例
"""

from simple_math_generator import SimpleMathProblemGenerator
from dotenv import load_dotenv
import os
import warnings

# Pydanticの警告を非表示にする
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def program_example():
    """プログラムでの使用例"""
    print("🔧 プログラムでの直接使用例")
    print("="*40)
    
    # APIキーの設定
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your-api-key-here":
        print("❌ APIキーが設定されていません")
        return
    
    # 生成器の初期化
    generator = SimpleMathProblemGenerator(api_key)
    
    # 1. 単一の類題生成
    print("\n📝 1. 単一の類題生成:")
    result = generator.generate_similar_problem("x + 5 = 12 を解きなさい", "中級")
    
    if "error" not in result:
        print("✅ 類題が生成されました:")
        print("-" * 50)
        print(result["generated_content"])
        print("-" * 50)
    
    # 2. 複数難易度での類題生成
    print("\n📚 2. 複数難易度での類題生成:")
    results = generator.generate_multiple_problems("x + 3 = 8 を解きなさい", ["初級", "中級", "上級"])
    
    # 3. セッション統計の表示
    print("\n📊 3. セッション統計:")
    generator.print_session_summary()

if __name__ == "__main__":
    program_example()
