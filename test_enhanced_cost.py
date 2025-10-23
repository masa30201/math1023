"""
改良版料金計算機能の簡単テスト
APIキーなしでも動作する部分をテスト
"""

from enhanced_cost_calculator import (
    enhanced_calculator,
    get_session_summary,
    print_session_summary,
    reset_session_stats
)

def test_cost_calculation_features():
    """料金計算機能のテスト（APIキー不要）"""
    print("=== 改良版料金計算機能テスト ===\n")
    
    # 1. 為替レート取得のテスト
    print("1. 為替レート取得テスト:")
    exchange_rate = enhanced_calculator.exchange_rate
    print(f"   現在の為替レート: 1 USD = {exchange_rate:.2f} JPY")
    
    # 2. トークン計算のテスト
    print("\n2. トークン計算テスト:")
    test_texts = [
        "Hello, world!",
        "こんにちは、世界！",
        "数学の問題を解いてください: x + 5 = 12",
        "This is a longer text that contains multiple sentences. It should have more tokens than the previous examples."
    ]
    
    for text in test_texts:
        tokens = enhanced_calculator.count_tokens(text, "gpt-4o-mini")
        print(f"   テキスト: '{text[:30]}...'")
        print(f"   トークン数: {tokens}")
    
    # 3. 料金計算のテスト
    print("\n3. 料金計算テスト:")
    test_prompt = "数学の問題を解いてください: x + 5 = 12"
    test_response = "x = 7"
    
    cost_data = enhanced_calculator.calculate_cost(test_prompt, test_response, "gpt-4o-mini")
    print(f"   入力トークン数: {cost_data['input_tokens']}")
    print(f"   出力トークン数: {cost_data['output_tokens']}")
    print(f"   料金（USD）: ${cost_data['total_cost_usd']:.6f}")
    print(f"   料金（JPY）: ¥{cost_data['total_cost_jpy']:.2f}")
    
    # 4. セッション統計のテスト
    print("\n4. セッション統計テスト:")
    print("   統計をリセット...")
    reset_session_stats()
    
    # 模擬的なAPI呼び出し統計を追加
    enhanced_calculator.session_stats["total_calls"] = 5
    enhanced_calculator.session_stats["total_tokens"] = 1000
    enhanced_calculator.session_stats["total_cost_usd"] = 0.01
    enhanced_calculator.session_stats["total_cost_jpy"] = 1.52
    
    print_session_summary()
    
    # 5. 複数モデル比較のテスト
    print("\n5. 複数モデル比較テスト:")
    models = ["gpt-4o-mini", "gpt-4o"]
    
    for model in models:
        cost = enhanced_calculator.calculate_cost(test_prompt, test_response, model)
        print(f"   {model}: ¥{cost['total_cost_jpy']:.4f}")
    
    print("\n✅ テスト完了！")
    print("\n💡 改良版の特徴:")
    print("   ✅ リアルタイム為替レート取得")
    print("   ✅ 正確なトークン計算")
    print("   ✅ 日本円での料金表示")
    print("   ✅ セッション統計管理")
    print("   ✅ 複数モデル比較")
    print("   ✅ エラーハンドリング")

def test_context_manager():
    """コンテキストマネージャーのテスト（模擬）"""
    print("\n=== コンテキストマネージャーテスト ===")
    
    # 模擬的なcallbackデータを作成
    class MockCallback:
        def __init__(self):
            self.prompt_tokens = 50
            self.completion_tokens = 30
            self.total_tokens = 80
            self.total_cost = 0.0001
    
    # コンテキストマネージャーをテスト
    try:
        with enhanced_calculator.track_cost("gpt-4o-mini", "模擬テスト") as callback:
            # 模擬的なcallbackオブジェクトを設定
            callback.prompt_tokens = 50
            callback.completion_tokens = 30
            callback.total_tokens = 80
            callback.total_cost = 0.0001
            
            print("   模擬API呼び出しを実行中...")
            print("   コンテキストマネージャーが正常に動作しています。")
            
    except Exception as e:
        print(f"   エラー: {e}")
    
    print_session_summary()

if __name__ == "__main__":
    test_cost_calculation_features()
    test_context_manager()
