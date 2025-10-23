"""
数学問題類題作成ツール（シンプル版）- 実際の使用例
問題検索機能を削除し、類題生成機能のみに特化
"""

import os
import warnings
from dotenv import load_dotenv
from simple_math_generator import SimpleMathProblemGenerator
from enhanced_cost_calculator import print_session_summary, reset_session_stats

# Pydanticの警告を非表示にする
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def main():
    """メイン実行関数"""
    print("🎓 数学問題類題作成ツール（シンプル版）")
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
    
    # 実際の使用例
    print("\n📚 類題生成例:")
    
    # 複数の問題でテスト
    test_problems = [
        "x + 5 = 12 を解きなさい。",
        "三角形の底辺が8cm、高さが6cmのとき、面積を求めなさい。",
        "y = 2x + 3 のグラフについて、x = 4 のときのyの値を求めなさい。"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n【例 {i}】")
        print(f"元の問題: {problem}")
        
        # 単一の類題生成
        generated = generator.generate_similar_problem(problem, "中級")
        
        if "error" not in generated:
            print("✅ 類題が生成されました:")
            print("-" * 50)
            print(generated["generated_content"])
            print("-" * 50)
            
            # 生成の料金表示
            if "cost_data" in generated:
                print(f"💰 生成料金: ¥{generated['cost_data']['total_cost_jpy']:.4f}")
        else:
            print(f"❌ 類題生成に失敗しました: {generated['error']}")
    
    # 複数難易度での類題生成例
    print("\n🎯 複数難易度での類題生成例:")
    sample_problem = "x + 3 = 8 を解きなさい。"
    print(f"元の問題: {sample_problem}")
    
    results = generator.generate_multiple_problems(sample_problem, ["初級", "中級", "上級"])
    
    # セッション統計の表示
    print("\n📊 セッション統計:")
    generator.print_session_summary()

def interactive_mode():
    """対話モード"""
    print("\n🎮 対話モード")
    print("="*30)
    
    # .envファイルを読み込み
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ APIキーが設定されていません")
        return
    
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
            break
        
        else:
            print("❌ 無効な選択です")

if __name__ == "__main__":
    try:
        # 対話モードの選択
        print("🎓 数学問題類題作成ツール（シンプル版）")
        print("="*50)
        print("1. デモ実行 + 対話モード")
        print("2. 対話モードのみ")
        
        mode = input("モードを選択してください (1-2): ").strip()
        
        if mode == "1":
            # メイン実行（デモ）
            main()
            # 対話モードの選択
            print("\n" + "="*50)
            use_interactive = input("対話モードを使用しますか？ (y/n): ").strip().lower()
            if use_interactive == 'y':
                interactive_mode()
        elif mode == "2":
            # 対話モードのみ
            interactive_mode()
        else:
            print("❌ 無効な選択です")
        
    except KeyboardInterrupt:
        print("\n👋 終了します")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
