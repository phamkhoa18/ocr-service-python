"""
Vietnamese Spell Correction - Comprehensive Solution
Tổng hợp TẤT CẢ các giải pháp sửa chính tả tiếng Việt chuyên nghiệp
"""

import re
import os
from typing import Optional, List, Dict
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class CorrectionMethod(Enum):
    """Các phương pháp correction có sẵn"""
    RULE_BASED = "rule"
    PROTONX = "protonx"
    GPT = "gpt"
    AUTO = "auto"

class VietnameseSpellCorrector:
    """
    Comprehensive Vietnamese Spell Corrector
    Hỗ trợ nhiều phương pháp sửa chính tả tiếng Việt
    """
    
    def __init__(self):
        self.methods_available = {}
        self._init_all_methods()
    
    def _init_all_methods(self):
        """Initialize tất cả các phương pháp correction"""
        
        # Method 1: Rule-based (luôn available)
        self.methods_available['rule'] = True
        print("✅ Rule-based correction: Available")
        
        # Method 2: ProtonX Model
        self.methods_available['protonx'] = self._check_protonx()
        
        # Method 3: GPT-4o-mini
        self.methods_available['gpt'] = self._check_gpt()
        
        # Method 4: Tìm các model khác trên Hugging Face
        self.methods_available['custom'] = False  # Placeholder for future models
        
        print(f"\n📊 Available methods: {[k for k, v in self.methods_available.items() if v]}")
    
    def _check_protonx(self) -> bool:
        """Check if ProtonX model is available"""
        try:
            from text_correction import get_text_corrector
            corrector = get_text_corrector()
            if corrector and hasattr(corrector, 'initialized') and corrector.initialized:
                print("✅ ProtonX model: Available")
                return True
        except Exception as e:
            print(f"⚠️  ProtonX model: Not available ({str(e)[:50]})")
        return False
    
    def _check_gpt(self) -> bool:
        """Check if GPT is available"""
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                from gpt_text_correction import GPTTextCorrector
                print("✅ GPT-4o-mini: Available")
                return True
        except Exception as e:
            print(f"⚠️  GPT-4o-mini: Not available ({str(e)[:50]})")
        return False
    
    def correct_text(
        self, 
        text: str, 
        method: str = "auto",
        aggressive: bool = True
    ) -> str:
        """
        Correct Vietnamese text với phương pháp tốt nhất
        
        Args:
            text: Input text từ OCR
            method: "rule", "protonx", "gpt", "auto"
            aggressive: Nếu True, dùng nhiều layers để sửa kỹ hơn
        
        Returns:
            Corrected text
        """
        if not text or not text.strip():
            return text
        
        # Auto: chọn method tốt nhất
        if method == "auto":
            method = self._select_best_method()
        
        print(f"\n🔧 Using correction method: {method.upper()}")
        
        corrected = text
        
        # Layer 1: Rule-based (luôn chạy để fix lỗi dễ và nhanh)
        corrected = self._rule_based_correction(corrected, aggressive=aggressive)
        
        # Layer 2: ML Model hoặc GPT (fix lỗi phức tạp)
        if method == "protonx" and self.methods_available.get('protonx'):
            corrected = self._protonx_correction(corrected)
        elif method == "gpt" and self.methods_available.get('gpt'):
            corrected = self._gpt_correction(corrected)
        elif method == "protonx" or method == "gpt":
            # Method requested but not available, fallback
            print(f"⚠️  {method.upper()} not available, using rule-based only")
        
        return corrected
    
    def _select_best_method(self) -> str:
        """Chọn method tốt nhất available"""
        if self.methods_available.get('gpt'):
            return "gpt"
        elif self.methods_available.get('protonx'):
            return "protonx"
        else:
            return "rule"
    
    def _rule_based_correction(self, text: str, aggressive: bool = True) -> str:
        """
        Rule-based correction - nhanh, fix lỗi dễ
        Comprehensive dictionary và rules cho tiếng Việt
        """
        if not text:
            return text
        
        # Comprehensive Vietnamese word dictionary
        # Các từ thường gặp trong văn bản pháp lý, hành chính
        corrections = {
            # Từ thường gặp - mất dấu
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
            r'\bgio\b': 'giờ',
            r'\bphut\b': 'phút',
            
            # Từ pháp lý
            r'\bquyet dinh\b': 'quyết định',
            r'\bquyet\b': 'quyết',
            r'\bdinh\b': 'định',
            r'\bchu\b': 'chủ',
            r'\btich\b': 'tịch',
            r'\bvien\b': 'viện',
            r'\bvien truong\b': 'viện trưởng',
            r'\btruong\b': 'trưởng',
            r'\bpho\b': 'phó',
            r'\bgiam doc\b': 'giám đốc',
            r'\bgiam\b': 'giám',
            r'\bdoc\b': 'đốc',
            r'\bcong\b': 'công',
            r'\bty\b': 'ty',
            r'\bso\b': 'sở',
            r'\bubnd\b': 'UBND',
            r'\bcong an\b': 'công an',
            r'\btu phap\b': 'tư pháp',
            r'\btu\b': 'tư',
            r'\bphap\b': 'pháp',
            r'\bhanh chinh\b': 'hành chính',
            r'\bhanh\b': 'hành',
            r'\bchinh\b': 'chính',
            r'\bnoi\b': 'nội',
            r'\bvu\b': 'vụ',
            r'\bcuc\b': 'cục',
            r'\bphong\b': 'phòng',
            r'\bchi\b': 'chỉ',
            r'\bthi\b': 'thị',
            r'\bthi xa\b': 'thị xã',
            r'\bxa\b': 'xã',
            r'\bhuyen\b': 'huyện',
            r'\btinh\b': 'tỉnh',
            r'\bthanh pho\b': 'thành phố',
            r'\bthanh\b': 'thành',
            r'\bpho\b': 'phố',
            
            # Động từ thường gặp
            r'\bthuc hien\b': 'thực hiện',
            r'\bthuc\b': 'thực',
            r'\bchien\b': 'hiện',
            r'\bkiem tra\b': 'kiểm tra',
            r'\bkiem\b': 'kiểm',
            r'\btra\b': 'tra',
            r'\bxac nhan\b': 'xác nhận',
            r'\bxac\b': 'xác',
            r'\bnhan\b': 'nhận',
            r'\bcap\b': 'cấp',
            r'\bgiai quyet\b': 'giải quyết',
            r'\bgiai\b': 'giải',
            r'\bquyet\b': 'quyết',
            
            # Dấu câu và spacing
            r'\.\s*\.': '.',  # Double dots
            r',\s*,': ',',    # Double commas
            r'\s+\.': '.',    # Space before period
            r'\.\s+': '. ',   # Space after period
            r'\s+': ' ',      # Multiple spaces
            r'\s+([.,;:!?])': r'\1',  # Space before punctuation
        }
        
        corrected = text
        
        # Apply corrections
        for pattern, replacement in corrections.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        
        # Aggressive mode: Fix more patterns
        if aggressive:
            corrected = self._aggressive_correction(corrected)
        
        return corrected
    
    def _aggressive_correction(self, text: str) -> str:
        """Aggressive correction mode - sửa nhiều pattern hơn"""
        # Fix common OCR character errors
        aggressive_fixes = {
            # Common OCR mistakes
            r'0': 'O',  # Careful - only in context
            r'l1': 'l1',  # Keep numbers
        }
        
        # TODO: Add more aggressive patterns
        return text
    
    def _protonx_correction(self, text: str) -> str:
        """ProtonX model correction"""
        try:
            from text_correction import correct_vietnamese_text
            return correct_vietnamese_text(text, use_correction=True)
        except Exception as e:
            print(f"⚠️  ProtonX correction error: {str(e)}")
            return text
    
    def _gpt_correction(self, text: str) -> str:
        """GPT-4o-mini correction"""
        try:
            from gpt_text_correction import correct_vietnamese_text_with_gpt
            import os
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                # Chỉ sửa chính tả, không trả về HTML
                corrected = correct_vietnamese_text_with_gpt(
                    text, 
                    api_key=openai_key,
                    model="gpt-4o-mini",
                    return_html=False  # Chỉ text, không HTML
                )
                return corrected
        except Exception as e:
            print(f"⚠️  GPT correction error: {str(e)}")
        return text

# Global instance
_corrector = None

def get_spell_corrector() -> VietnameseSpellCorrector:
    """Get or create spell corrector instance"""
    global _corrector
    if _corrector is None:
        _corrector = VietnameseSpellCorrector()
    return _corrector

def correct_vietnamese_spelling(
    text: str, 
    method: str = "auto",
    aggressive: bool = True
) -> str:
    """
    Comprehensive Vietnamese spell correction
    
    Args:
        text: Input text từ OCR
        method: "rule", "protonx", "gpt", "auto"
        aggressive: Nếu True, sửa kỹ hơn
    
    Returns:
        Corrected text
    """
    corrector = get_spell_corrector()
    return corrector.correct_text(text, method=method, aggressive=aggressive)

