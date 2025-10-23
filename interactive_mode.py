"""
数学問題類題作成ツール（対話モード専用）
デモをスキップしていきなり問題入力
"""

import os
import warnings
from dotenv import load_dotenv
from simple_math_generator import SimpleMathProblemGenerator
from enhanced_cost_calculator import print_session_summary, reset_session_stats

# Pydanticの警告を非表示にする
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def main():
    """メイン実行関数（対話モードのみ）"""
    print("🎓 数学問題類題作成ツール（対話モード）")
    print("="*50)
    
    # .envファイルを読み込み
    load_dotenv()
    
    # APIキーの確認
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ APIキーが設定されていません")
        print("以下の手順でAPIキーを設定してください:")
        print("1. .envファイルを作成")
        print("2. OPENAI_API_KEY=sk-your-actual-key を記述")
        return
    
    print("✅ APIキーが設定されています")
    
    # セッション統計をリセット
    reset_session_stats()
    
    # シンプル版数学問題生成器の初期化
    generator = SimpleMathProblemGenerator(api_key)
    
    print("✅ 準備完了！以下の操作ができます:")
    print("1. 類題生成")
    print("2. 終了")
    
    while True:
        print("\n" + "-"*30)
        choice = input("操作を選択してください (1-2): ").strip()
        
        if choice == "1":
            problem = input("類題を生成したい問題を入力してください: ").strip()
            difficulty = input("難易度を選択してください (初級/中級/上級): ").strip()
            if problem and difficulty:
                generated = generator.generate_similar_problem(problem, difficulty)
                if "error" not in generated:
                    print("✅ 類題が生成されました:")
                    print("-" * 50)
                    print(generated["generated_content"])
                    print("-" * 50)
                else:
                    print(f"❌ 生成に失敗しました: {generated['error']}")
        
        elif choice == "2":
            print("👋 終了します")
            # セッション統計の表示
            print_session_summary()
            break
        
        else:
            print("❌ 無効な選択です")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 終了します")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
