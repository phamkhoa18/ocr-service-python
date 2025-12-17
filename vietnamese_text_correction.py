"""
Vietnamese Text Correction - Multiple Solutions
Tổng hợp các giải pháp sửa chính tả tiếng Việt cho OCR output
"""

import re
import os
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class VietnameseTextCorrector:
    """
    Tổng hợp nhiều phương pháp sửa chính tả tiếng Việt
    """
    
    def __init__(self):
        self.correction_methods = []
        self._init_methods()
    
    def _init_methods(self):
        """Initialize các phương pháp correction"""
        # Method 1: Rule-based (nhanh, fix lỗi dễ)
        self.rule_based_available = True
        
        # Method 2: ML Model (ProtonX, nếu available)
        self.ml_model_available = False
        self.ml_model = None
        try:
            from text_correction import get_text_corrector
            self.ml_model = get_text_corrector()
            if self.ml_model and self.ml_model.initialized:
                self.ml_model_available = True
                print("✅ ML Text Correction model (ProtonX) available")
        except Exception as e:
            print(f"⚠️  ML model không available: {str(e)}")
        
        # Method 3: GPT (nếu có API key)
        self.gpt_available = False
        try:
            from gpt_text_correction import GPTTextCorrector
            import os
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.gpt_available = True
                print("✅ GPT Text Correction available")
        except Exception as e:
            print(f"⚠️  GPT không available: {str(e)}")
    
    def correct_text(self, text: str, method: str = "auto") -> str:
        """
        Correct Vietnamese text với nhiều phương pháp
        
        Args:
            text: Input text từ OCR
            method: "rule", "ml", "gpt", "auto" (tự chọn best available)
        
        Returns:
            Corrected text
        """
        if not text or not text.strip():
            return text
        
        # Auto: chọn method tốt nhất available
        if method == "auto":
            if self.ml_model_available:
                method = "ml"
            elif self.gpt_available:
                method = "gpt"
            else:
                method = "rule"
        
        # Apply corrections
        corrected = text
        
        # Layer 1: Rule-based (luôn chạy đầu tiên để fix lỗi dễ)
        corrected = self._rule_based_correction(corrected)
        
        # Layer 2: ML/GPT (fix lỗi phức tạp)
        if method == "ml" and self.ml_model_available:
            corrected = self._ml_correction(corrected)
        elif method == "gpt" and self.gpt_available:
            corrected = self._gpt_correction(corrected)
        
        return corrected
    
    def _rule_based_correction(self, text: str) -> str:
        """
        Rule-based correction - nhanh, fix lỗi dễ
        - Fix dấu thanh điệu
        - Fix dấu câu
        - Fix từ thường gặp
        """
        if not text:
            return text
        
        # Fix common OCR errors
        corrections = {
            # Fix mất dấu trong từ thường gặp
            r'\bkhong\b': 'không',
            r'\bco\b': 'có',
            r'\btoi\b': 'tôi',
            r'\bdoi\b': 'đôi',
            r'\bdao\b': 'đào',
            r'\bdoan\b': 'đoàn',
            r'\bdoi\b': 'đội',
            r'\bvay\b': 'vậy',
            r'\bday\b': 'đây',
            r'\bnay\b': 'này',
            r'\bvoi\b': 'với',
            r'\bden\b': 'đến',
            r'\bduoc\b': 'được',
            r'\bduoi\b': 'dưới',
            r'\btren\b': 'trên',
            r'\bgiua\b': 'giữa',
            r'\bngoai\b': 'ngoài',
            r'\btruoc\b': 'trước',
            r'\bsau\b': 'sau',
            r'\bnam\b': 'năm',
            r'\bthang\b': 'tháng',
            r'\bngay\b': 'ngày',
            
            # Fix dấu câu
            r'\.\s*\.': '.',  # Double dots
            r',\s*,': ',',    # Double commas
            r'\s+\.': '.',    # Space before period
            r'\.\s+': '. ',   # Space after period
            
            # Fix spacing
            r'\s+': ' ',      # Multiple spaces
            r'\s+([.,;:!?])': r'\1',  # Space before punctuation
        }
        
        corrected = text
        for pattern, replacement in corrections.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        
        return corrected
    
    def _ml_correction(self, text: str) -> str:
        """ML model correction (ProtonX)"""
        if not self.ml_model_available or not self.ml_model:
            return text
        
        try:
            from text_correction import correct_vietnamese_text
            return correct_vietnamese_text(text, use_correction=True)
        except Exception as e:
            print(f"⚠️  ML correction error: {str(e)}")
            return text
    
    def _gpt_correction(self, text: str) -> str:
        """GPT correction"""
        if not self.gpt_available:
            return text
        
        try:
            from gpt_text_correction import correct_vietnamese_text_with_gpt
            import os
            openai_key = os.getenv('OPENAI_API_KEY')
            return correct_vietnamese_text_with_gpt(text, api_key=openai_key)
        except Exception as e:
            print(f"⚠️  GPT correction error: {str(e)}")
            return text

# Global instance
_corrector = None

def get_corrector() -> VietnameseTextCorrector:
    """Get or create corrector instance"""
    global _corrector
    if _corrector is None:
        _corrector = VietnameseTextCorrector()
    return _corrector

def correct_vietnamese_text_advanced(text: str, method: str = "auto") -> str:
    """
    Advanced Vietnamese text correction với nhiều phương pháp
    
    Args:
        text: Input text từ OCR
        method: "rule", "ml", "gpt", "auto"
    
    Returns:
        Corrected text
    """
    corrector = get_corrector()
    return corrector.correct_text(text, method=method)

