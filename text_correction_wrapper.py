"""
Text Correction Wrapper - Sử dụng ProtonX Legal Text Correction Model
Flow: PaddleOCR → ProtonX Model → Trả về text đã sửa chính tả tiếng Việt
"""

def correct_vietnamese_text(text, use_correction=True, use_gpu=False, api_key=None):
    """
    Correct Vietnamese text bằng ProtonX Legal Text Correction Model
    Sau khi PaddleOCR lấy text → Gọi ProtonX để sửa chính tả tiếng Việt chuẩn
    
    Args:
        text: Input text từ PaddleOCR
        use_correction: Enable/disable correction
        use_gpu: Use GPU if available (for ProtonX model)
        api_key: Not used (kept for compatibility)
        
    Returns:
        Corrected text từ ProtonX model
    """
    if not use_correction or not text or not text.strip():
        return text
    
    # Sử dụng ProtonX Legal Text Correction model
    try:
        from text_correction import correct_vietnamese_text as protonx_correct
        
        print("🔧 Đang gọi ProtonX Legal Text Correction model để sửa chính tả tiếng Việt...")
        print("   Model: protonx-models/protonx-legal-tc")
        print("   ⚠️  CHỈ SỬA CHÍNH TẢ, giữ nguyên nội dung và layout")
        
        # Gọi ProtonX để sửa chính tả
        corrected = protonx_correct(text, use_correction=True, use_gpu=use_gpu)
        
        if corrected and corrected.strip():
            print("✅ Đã sửa chính tả thành công với ProtonX model")
            return corrected
        else:
            print("⚠️  ProtonX trả về text rỗng, giữ nguyên text gốc")
            return text
            
    except ImportError as e:
        print(f"⚠️  Module text_correction không khả dụng: {str(e)}")
        print("💡 Cài đặt: pip install transformers torch sentencepiece accelerate")
        print("   Hoặc kiểm tra xem torch có load được không (có thể cần Visual C++ Redistributable trên Windows)")
        return text
    except Exception as e:
        print(f"⚠️  Lỗi khi gọi ProtonX model: {str(e)}")
        print("💡 Kiểm tra:")
        print("   - transformers, torch đã được cài đặt chưa")
        print("   - Model có thể download từ Hugging Face không (cần internet)")
        print("   - GPU/CUDA có available không (nếu use_gpu=True)")
        return text  # Return original text on error

