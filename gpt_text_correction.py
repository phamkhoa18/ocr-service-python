"""
GPT-based Vietnamese Text Correction
Fallback khi ProtonX model không available
Sử dụng GPT-4o-mini để chỉnh sửa tiếng Việt sau OCR
"""

import os
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Optional import for OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

class GPTTextCorrector:
    """GPT-based Vietnamese Text Corrector"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize GPT text corrector
        
        Args:
            api_key: OpenAI API key (if None, will try to get from env)
            model: Model to use (default: gpt-4o-mini)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("openai package không khả dụng. Cài đặt: pip install openai")
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key không được tìm thấy. Set OPENAI_API_KEY trong file .env hoặc environment variable.")
        
        self.model = model
        self.client = OpenAI(api_key=self.api_key)
        self.initialized = True
    
    def correct_text(self, text: str) -> str:
        """
        Correct Vietnamese text using GPT and convert to HTML
        
        Args:
            text: Input text to correct (with layout markers like tabs, spacing)
            
        Returns:
            Corrected HTML (ready to load into TinyMCE)
        """
        if not text or not text.strip():
            return text
        
        print(text)
        
        try:
            # Prompt được thiết kế để GPT trả về HTML với layout được giữ nguyên và chính tả đã sửa CHUẨN
            prompt = f"""Bạn là chuyên gia sửa CHÍNH TẢ tiếng Việt CHUẨN XÁC.
Nhiệm vụ: Sửa CHÍNH TẢ (dấu, từ sai, ngắt từ) trong văn bản OCR và trả về HTML, giữ nguyên 100% layout.

🔧 QUY TẮC SỬA CHÍNH TẢ TIẾNG VIỆT CHUẨN

1. QUY TẮC DẤU CÂU VÀ DẤU TIẾNG VIỆT:
   - "quyet dinh" → "quyết định" (đầy đủ dấu)
   - "VIEN" → "VIỆN" (thêm dấu)
   - "DAK LAK" → "ĐẮK LẮK" (đúng tên địa danh)
   - "phap luat" → "pháp luật"
   - "hanh chinh" → "hành chính"
   - "tai chinh" → "tài chính"
   - "toa an" → "tòa án"
   - "van ban" → "văn bản"
   - "chu the" → "chủ thể"
   - "quyen han" → "quyền hạn"

2. QUY TẮC NGẮT TỪ VÀ DẤU CÁCH:
   - "quyetdinh" → "quyết định" (tách từ đúng)
   - "vanban" → "văn bản"
   - "toaan" → "tòa án"
   - "hieuluat" → "hiệu lực"
   - Giữ nguyên khoảng cách giữa các từ nếu đã đúng

3. QUY TẮC VIẾT HOA:
   - Giữ nguyên viết hoa đầu câu, tên riêng
   - "VIEN KIEM SAT" → "VIỆN KIỂM SÁT" (giữ hoa, chỉ sửa dấu)
   - "UBND" → "UBND" (viết tắt giữ nguyên)

4. QUY TẮC SỐ VÀ KÝ TỰ:
   - Giữ nguyên số: "2024", "123"
   - Giữ nguyên ký tự đặc biệt: "-", "+", "•", ":", ";", "(", ")", "[", "]"
   - Giữ nguyên ngày tháng: "01/01/2024" → "01/01/2024"

5. CHỈ SỬA LỖI CHÍNH TẢ, KHÔNG:
   ❌ Thêm từ
   ❌ Xóa từ  
   ❌ Thay đổi nghĩa
   ❌ Paraphrase
   ❌ Viết lại câu
   ❌ Thay đổi thứ tự từ
   ❌ Thêm/bớt dòng
   ❌ Gộp/tách dòng

📋 QUY TẮC HTML:
1. Mỗi dòng văn bản gốc → một thẻ <p>
   Kể cả dòng bắt đầu bằng "-", "+", "•", số thứ tự → phải xuống dòng bằng <p>…</p>

2. Dòng trống → <p>&nbsp;</p>

3. Khoảng trắng (spaces, TAB) → giữ nguyên bằng &nbsp;

4. Căn giữa / căn phải:
   - Nếu dòng có dấu hiệu căn giữa → <p style="text-align:center">…</p>
   - Nếu dòng có dấu hiệu căn phải → <p style="text-align:right">…</p>

5. KHÔNG sử dụng <table>, <tr>, <td> (dùng <p> với &nbsp; để giữ layout)

6. Giữ nguyên số dòng, vị trí, thứ tự

📥 INPUT:
{text}

📤 OUTPUT:
Trả về HTML thuần với các thẻ <p>.
- Mỗi dòng trong input → một <p>
- Dòng rỗng → <p>&nbsp;</p>
- Giữ đúng layout bằng &nbsp; và style="text-align:center/right" nếu cần
- KHÔNG giải thích gì thêm, chỉ trả về HTML

⚠️ LƯU Ý QUAN TRỌNG:
- Chỉ sửa DẤU và NGẮT TỪ, không thay đổi nội dung
- Giữ nguyên 100% layout và số dòng
- Sửa CHÍNH XÁC theo quy tắc chính tả tiếng Việt chuẩn
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Bạn là chuyên gia chỉnh sửa CHÍNH TẢ tiếng Việt CHUẨN XÁC và chuyển đổi sang HTML.\n\nNHIỆM VỤ:\n1. SỬA CHÍNH TẢ (dấu, từ sai, ngắt từ) theo quy tắc tiếng Việt chuẩn\n2. GIỮ NGUYÊN LAYOUT (bảng, cột, spacing, alignment, indentation)\n3. TRẢ VỀ HTML hợp lệ để load vào TinyMCE editor\n\nNGHIÊM CẤM:\n❌ Thêm/bớt từ\n❌ Thay đổi nội dung\n❌ Viết lại/paraphrase\n❌ Thay đổi layout (số dòng, vị trí, thứ tự)\n❌ Thêm giải thích hoặc markdown code blocks\n\nQUY TẮC:\n- Chỉ sửa lỗi chính tả (dấu, ngắt từ)\n- Giữ nguyên 100% nội dung và layout gốc\n- Trả về HTML clean, không có markdown code blocks\n- Sửa CHÍNH XÁC theo quy tắc chính tả tiếng Việt chuẩn"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.0,  # Zero temperature để đảm bảo không sáng tạo, chỉ sửa chính tả
                max_tokens=3000,  # Tăng để đủ cho văn bản dài
                top_p=0.1,  # Nghiêm ngặt hơn để tránh sáng tạo
            )
            
            corrected_html = response.choices[0].message.content.strip()
            print(f"📝 GPT Response (first 500 chars): {corrected_html[:500]}")
            print(f"📝 GPT Response length: {len(corrected_html)} characters")
            
            # Remove any potential markdown code blocks (```html or ```)
            if corrected_html.startswith("```"):
                lines = corrected_html.split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]  # Remove first line (```html or ```)
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]  # Remove last line (```)
                corrected_html = "\n".join(lines).strip()
            
            # Remove any leading/trailing whitespace but keep HTML structure
            corrected_html = corrected_html.strip()
            
            return corrected_html
            
        except Exception as e:
            print(f"⚠️  Lỗi khi sửa văn bản với GPT: {str(e)}")
            return text  # Return original text on error
    
    def correct_long_text(self, text: str, chunk_size: int = 2000) -> str:
        """
        Correct long text by splitting into chunks
        
        Args:
            text: Long text to correct
            chunk_size: Approximate chunk size in characters
            
        Returns:
            Corrected text
        """
        if not text or not text.strip():
            return text
        
        # Split by sentences first
        sentences = self._split_into_sentences(text)
        
        # Group sentences into chunks
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        # Correct each chunk
        corrected_chunks = []
        for chunk in chunks:
            corrected = self.correct_text(chunk)
            corrected_chunks.append(corrected)
        
        return "\n".join(corrected_chunks)
    
    def _split_into_sentences(self, text: str) -> list:
        """Split text into sentences"""
        import re
        
        # Split by common sentence delimiters
        sentences = re.split(r'([.!?]\s+)', text)
        
        # Recombine sentences with their delimiters
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                result.append(sentences[i] + sentences[i + 1])
            else:
                result.append(sentences[i])
        
        if len(sentences) % 2 == 1:
            result.append(sentences[-1])
        
        # Also split by newlines
        final_result = []
        for sentence in result:
            if '\n' in sentence:
                final_result.extend(sentence.split('\n'))
            else:
                final_result.append(sentence)
        
        return [s.strip() for s in final_result if s.strip()]

# Global instance
_gpt_corrector = None

def get_gpt_corrector(api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
    """Get or create GPT corrector instance"""
    global _gpt_corrector
    if _gpt_corrector is None:
        _gpt_corrector = GPTTextCorrector(api_key=api_key, model=model)
    return _gpt_corrector

def correct_vietnamese_text_with_gpt(text: str, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> str:
    """
    Correct Vietnamese text using GPT API
    
    Args:
        text: Input text
        api_key: OpenAI API key
        model: Model to use
        
    Returns:
        Corrected text
    """
    if not text:
        return text
    
    try:
        corrector = get_gpt_corrector(api_key=api_key, model=model)
        if len(text) > 2000:
            return corrector.correct_long_text(text)
        else:
            return corrector.correct_text(text)
    except Exception as e:
        print(f"⚠️  GPT text correction failed: {str(e)}")
        return text


