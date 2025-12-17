"""
Test script đơn giản để kiểm tra ProtonX model có hoạt động không
"""

import sys

def test_protonx():
    print("="*60)
    print("🧪 TEST PROTONX MODEL - SIMPLE")
    print("="*60)
    
    # Test text có lỗi chính tả
    test_text = "toi khong co gi de noi"
    expected = "tôi không có gì để nói"
    
    print(f"\n📝 Test text: {test_text}")
    print(f"📝 Expected: {expected}")
    
    try:
        from text_correction import correct_vietnamese_text
        
        print("\n→ Gọi correct_vietnamese_text...")
        result = correct_vietnamese_text(test_text, use_correction=True, use_gpu=False)
        
        print(f"\n✅ Kết quả: {result}")
        print(f"📊 Input length: {len(test_text)}")
        print(f"📊 Output length: {len(result)}")
        print(f"📊 Giống nhau: {test_text == result}")
        
        if test_text != result:
            print("✅ Model đã sửa chính tả!")
        else:
            print("⚠️  Model trả về text gốc (có thể không sửa được hoặc đã đúng)")
        
        return True
    except Exception as e:
        import traceback
        print(f"\n❌ Lỗi: {str(e)}")
        print("\n📋 Chi tiết:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_protonx()
    sys.exit(0 if success else 1)

