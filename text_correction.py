"""
Vietnamese Text Correction Module
Sử dụng ProtonX Legal Text Correction model để chỉnh sửa văn bản sau OCR
Model: protonx-models/protonx-legal-tc
"""

import re

# Optional imports - không fail nếu không có torch/transformers
TORCH_AVAILABLE = False
torch = None
AutoTokenizer = None
AutoModelForSeq2SeqLM = None

try:
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: torch/transformers không khả dụng. Text correction sẽ bị tắt.")
    print(f"   Error: {str(e)}")
    TORCH_AVAILABLE = False
except OSError as e:
    print(f"⚠️  Warning: Lỗi khi load torch DLL. Text correction sẽ bị tắt.")
    print(f"   Error: {str(e)}")
    print(f"💡 Gợi ý: Thử cài lại torch hoặc tắt text correction.")
    TORCH_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Warning: Lỗi không xác định khi import torch. Text correction sẽ bị tắt.")
    print(f"   Error: {str(e)}")
    TORCH_AVAILABLE = False

class VietnameseTextCorrector:
    """Vietnamese Text Corrector using ProtonX Legal TC model"""
    
    def __init__(self, model_path="protonx-models/protonx-legal-tc", use_gpu=False):
        """
        Initialize the text correction model
        
        Args:
            model_path: Hugging Face model path
            use_gpu: Use GPU if available
        """
        self.model_path = model_path
        self.use_gpu = use_gpu
        self.model = None
        self.tokenizer = None
        self.device = None
        self.initialized = False
        
    def _initialize_model(self):
        """Lazy initialization of the model"""
        if self.initialized:
            return
        
        # Check if torch is available
        if not TORCH_AVAILABLE:
            print("❌ torch/transformers không khả dụng. Text correction không thể sử dụng.")
            self.initialized = False
            return
            
        try:
            print("🔄 Đang tải ProtonX Text Correction model...")
            print(f"   Model: {self.model_path}")
            print("   ⚠️  Lần đầu tiên sẽ download model (~500MB-1GB), cần internet!")
            
            # Set device
            self.device = torch.device("cuda" if (self.use_gpu and torch.cuda.is_available()) else "cpu")
            print(f"   Device: {self.device}")
            
            # Load tokenizer
            print("   → Đang tải tokenizer...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            print("   ✅ Tokenizer đã tải xong")
            
            # Load model
            print("   → Đang tải model (có thể mất vài phút)...")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_path)
            print("   ✅ Model đã tải xong")
            
            # Move to device
            print(f"   → Đang chuyển model sang {self.device}...")
            self.model.to(self.device)
            self.model.eval()
            print(f"   ✅ Model đã chuyển sang {self.device}")
            
            self.initialized = True
            print("✅ ProtonX Text Correction model đã sẵn sàng!")
            
        except Exception as e:
            import traceback
            print(f"❌ Lỗi khi khởi tạo Text Correction model: {str(e)}")
            print("⚠️  Text correction sẽ bị tắt. OCR sẽ trả về text gốc.")
            print("\n📋 Chi tiết lỗi:")
            traceback.print_exc()
            self.initialized = False
    
    def correct_text(self, text, max_length=128):
        """
        Correct Vietnamese text
        
        Args:
            text: Input text to correct
            max_length: Maximum sequence length (default: 128 tokens)
            
        Returns:
            Corrected text
        """
        if not text or not text.strip():
            return text
        
        print(f"📝 Input text length: {len(text)} chars")
        print(f"📝 Input text preview: {text[:100]}...")
        
        # Initialize model if not already done
        if not self.initialized:
            print("🔄 Model chưa được khởi tạo, đang khởi tạo...")
            try:
                self._initialize_model()
            except Exception as e:
                print(f"❌ Không thể khởi tạo model: {str(e)}")
                return text  # Return original text if model fails
        
        if not self.initialized:
            print("⚠️  Model không được khởi tạo thành công, trả về text gốc")
            return text
        
        print(f"✅ Model đã sẵn sàng, đang sửa chính tả...")
        
        try:
            # Split text into sentences/chunks if too long
            # Model max length is 128 tokens
            sentences = self._split_into_sentences(text)
            print(f"📝 Đã tách thành {len(sentences)} câu")
            
            corrected_parts = []
            
            for idx, sentence in enumerate(sentences):
                if not sentence.strip():
                    corrected_parts.append(sentence)
                    continue
                
                print(f"   → Đang sửa câu {idx + 1}/{len(sentences)}: {sentence[:50]}...")
                
                # Truncate if too long (max 128 tokens)
                inputs = self.tokenizer(
                    sentence,
                    return_tensors="pt",
                    truncation=True,
                    max_length=max_length,
                    padding=True
                ).to(self.device)
                
                # Generate corrected text
                with torch.no_grad():
                    outputs = self.model.generate(
                        **inputs,
                        num_beams=10,
                        max_new_tokens=max_length,
                        length_penalty=1.0,
                        early_stopping=True,
                        repetition_penalty=1.2,
                        no_repeat_ngram_size=2,
                        pad_token_id=self.tokenizer.pad_token_id,
                        eos_token_id=self.tokenizer.eos_token_id,
                    )
                
                corrected = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                print(f"      ✅ Đã sửa: {corrected[:50]}...")
                corrected_parts.append(corrected)
            
            # Join corrected parts
            corrected_text = "\n".join(corrected_parts)
            
            print(f"✅ Đã sửa xong, output length: {len(corrected_text)} chars")
            print(f"📝 Output preview: {corrected_text[:100]}...")
            
            return corrected_text
            
        except Exception as e:
            import traceback
            print(f"⚠️  Lỗi khi correct text: {str(e)}")
            print("📋 Chi tiết lỗi:")
            traceback.print_exc()
            return text  # Return original text on error
    
    def correct_long_text(self, text, chunk_size=128, overlap=20):
        """
        Correct long text by splitting into chunks và xử lý từng phần
        
        Args:
            text: Long text to correct
            chunk_size: Size of each chunk in tokens (default: 128)
            overlap: Overlap between chunks in tokens (default: 20)
            
        Returns:
            Corrected text
        """
        if not text or not text.strip():
            return text
        
        print(f"📝 Text dài ({len(text)} chars), đang chia nhỏ để xử lý...")
        
        # Check if torch is available
        if not TORCH_AVAILABLE:
            return text  # Return original if torch not available
        
        # Initialize model if not already done
        if not self.initialized:
            print("→ Model chưa được khởi tạo, đang khởi tạo...")
            self._initialize_model()
        
        if not self.initialized:
            print("⚠️  Model không được khởi tạo, trả về text gốc")
            return text  # Return original if initialization failed
        
        try:
            # Split text by lines first (giữ nguyên cấu trúc)
            lines = text.split('\n')
            print(f"📝 Đã tách thành {len(lines)} dòng")
            
            # Process each line (hoặc group of lines)
            corrected_lines = []
            
            for line_idx, line in enumerate(lines):
                if not line.strip():
                    corrected_lines.append(line)  # Giữ nguyên dòng trống
                    continue
                
                # Nếu dòng quá dài, chia nhỏ hơn
                if len(line) > 200:  # Nếu dòng quá 200 ký tự
                    print(f"   → Dòng {line_idx + 1} quá dài ({len(line)} chars), đang chia nhỏ...")
                    
                    # Chia dòng thành các câu nhỏ hơn
                    sentences = self._split_into_sentences(line)
                    corrected_line_parts = []
                    
                    for sentence in sentences:
                        if not sentence.strip():
                            continue
                        
                        # Sửa từng câu
                        try:
                            corrected_sentence = self.correct_text(sentence, max_length=chunk_size)
                            corrected_line_parts.append(corrected_sentence)
                        except Exception as e:
                            print(f"      ⚠️  Lỗi khi sửa câu: {str(e)}")
                            corrected_line_parts.append(sentence)  # Giữ nguyên nếu lỗi
                    
                    corrected_line = " ".join(corrected_line_parts)
                    corrected_lines.append(corrected_line)
                else:
                    # Dòng ngắn, sửa trực tiếp
                    try:
                        corrected_line = self.correct_text(line, max_length=chunk_size)
                        corrected_lines.append(corrected_line)
                    except Exception as e:
                        print(f"   ⚠️  Lỗi khi sửa dòng {line_idx + 1}: {str(e)}")
                        corrected_lines.append(line)  # Giữ nguyên nếu lỗi
            
            result = "\n".join(corrected_lines)
            print(f"✅ Đã xử lý xong {len(corrected_lines)} dòng")
            
            return result
            
        except Exception as e:
            import traceback
            print(f"⚠️  Lỗi khi correct long text: {str(e)}")
            print("📋 Chi tiết lỗi:")
            traceback.print_exc()
            return text
    
    def _split_into_sentences(self, text):
        """Split text into sentences"""
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
    
    def _create_chunks(self, sentences, chunk_size, overlap):
        """Create overlapping chunks from sentences"""
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(self.tokenizer.encode(sentence, add_special_tokens=False))
            
            if current_length + sentence_length > chunk_size and current_chunk:
                chunks.append(current_chunk)
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(self.tokenizer.encode(s, add_special_tokens=False)) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

# Global instance (lazy loading)
_text_corrector = None

def get_text_corrector(use_gpu=False, model_path="protonx-models/protonx-legal-tc"):
    """Get or create text corrector instance (singleton)"""
    global _text_corrector
    if _text_corrector is None:
        _text_corrector = VietnameseTextCorrector(model_path=model_path, use_gpu=use_gpu)
    return _text_corrector

def correct_vietnamese_text(text, use_correction=True, use_gpu=False):
    """
    Correct Vietnamese text using ProtonX model
    Tự động xử lý text ngắn và text dài
    
    Args:
        text: Input text (có thể rất dài)
        use_correction: Enable/disable correction
        use_gpu: Use GPU if available
        
    Returns:
        Corrected text
    """
    if not use_correction or not text or not text.strip():
        print("⚠️  Text correction bị tắt hoặc text rỗng")
        return text
    
    print(f"\n{'='*60}")
    print("🔧 BẮT ĐẦU SỬA CHÍNH TẢ TIẾNG VIỆT")
    print(f"{'='*60}")
    print(f"📝 Input length: {len(text)} chars")
    print(f"📝 Input preview: {text[:200]}..." if len(text) > 200 else f"📝 Input: {text}")
    
    try:
        corrector = get_text_corrector(use_gpu=use_gpu)
        
        if not corrector.initialized:
            print("⚠️  Model chưa được khởi tạo, đang khởi tạo...")
            corrector._initialize_model()
        
        if not corrector.initialized:
            print("❌ Model không thể khởi tạo, trả về text gốc")
            return text
        
        # Tự động chọn method dựa trên độ dài text
        # Text dài (>1000 chars hoặc >500 chars) → dùng correct_long_text
        # Text ngắn → dùng correct_text
        if len(text) > 1000:
            print("→ Text rất dài (>1000 chars), dùng correct_long_text...")
            result = corrector.correct_long_text(text, chunk_size=128)
        elif len(text) > 500:
            print("→ Text dài (>500 chars), dùng correct_long_text...")
            result = corrector.correct_long_text(text, chunk_size=128)
        else:
            print("→ Text ngắn, dùng correct_text...")
            result = corrector.correct_text(text, max_length=128)
        
        print(f"\n{'='*60}")
        print(f"✅ HOÀN THÀNH SỬA CHÍNH TẢ")
        print(f"{'='*60}")
        print(f"📝 Output length: {len(result)} chars")
        print(f"📝 Output preview: {result[:200]}..." if len(result) > 200 else f"📝 Output: {result}")
        
        return result
    except Exception as e:
        import traceback
        print(f"\n❌ Text correction failed: {str(e)}")
        print("📋 Chi tiết lỗi:")
        traceback.print_exc()
        return text  # Return original on error

