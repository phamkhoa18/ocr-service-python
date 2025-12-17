# Giải pháp Sửa Chính Tả Tiếng Việt cho OCR

## Vấn đề hiện tại

OCR output thường có lỗi chính tả (mất dấu, sai dấu, thiếu dấu, từ sai). Cần một giải pháp để sửa chính tả tiếng Việt chuẩn.

## Các giải pháp đề xuất

### 1. VIETOCR (OCR Engine - Không phải Text Correction)

**VIETOCR** là OCR engine chuyên cho tiếng Việt:
- **Mục đích**: Nhận dạng văn bản từ ảnh (thay thế/bổ sung PaddleOCR)
- **Không có**: Chức năng sửa chính tả tự động
- **Ưu điểm**: Có thể cho kết quả OCR tốt hơn PaddleOCR cho tiếng Việt
- **Nhược điểm**: Vẫn cần text correction model sau đó

**Kết luận**: VIETOCR có thể cải thiện OCR quality, nhưng vẫn cần text correction.

### 2. Các mô hình Text Correction tiếng Việt

#### A. Sequence-to-Sequence Models (Như ProtonX)
- **protonx-models/protonx-legal-tc**: Đã thử, nhưng gặp vấn đề load
- **Pros**: Chuyên cho văn bản pháp lý, sửa chính tả tốt
- **Cons**: Cần torch/transformers, model lớn (~1GB)

#### B. PhoBERT-based Models
- **vinai/phobert-base**: BERT cho tiếng Việt
- **vinai/phobert-large**: BERT lớn hơn, tốt hơn
- Có thể fine-tune cho text correction

#### C. Rule-based + Dictionary
- Sử dụng từ điển tiếng Việt
- Rules cho dấu câu, dấu thanh
- Nhẹ, nhanh, nhưng ít chính xác hơn ML models

### 3. Giải pháp đề xuất: Multi-layered Approach

```
OCR Output (PaddleOCR/VIETOCR)
    ↓
Text Correction Layer 1: Rule-based (nhanh, fix lỗi dễ)
    ↓
Text Correction Layer 2: ML Model (chính xác, fix lỗi phức tạp)
    ↓
Final Corrected Text
```

## Implementation Options

### Option 1: VIETOCR + Text Correction
```python
# Dùng VIETOCR thay PaddleOCR
from vietocr.tool.predictor import Predictor
from vietocr.tool.config import Cfg

# OCR với VIETOCR
ocr_result = vietocr_ocr(image)

# Text correction
corrected = correct_vietnamese_text(ocr_result)
```

### Option 2: PaddleOCR + Better Text Correction
```python
# Giữ PaddleOCR
ocr_result = paddleocr_ocr(image)

# Text correction tốt hơn
corrected = advanced_vietnamese_correction(ocr_result)
```

### Option 3: Hybrid OCR + Multi-layer Correction
```python
# Cho phép chọn OCR engine
if use_vietocr:
    ocr_result = vietocr_ocr(image)
else:
    ocr_result = paddleocr_ocr(image)

# Multi-layer correction
corrected = multi_layer_correction(ocr_result)
```

## Recommended Solution

**Tôi đề xuất Option 2: PaddleOCR + Better Text Correction**

Vì:
1. PaddleOCR đã ổn định và tốt
2. Text correction là phần quan trọng hơn
3. Có thể tìm model text correction tốt hơn

## Next Steps

1. Tìm và test các text correction models tốt nhất
2. Implement rule-based layer (nhanh)
3. Integrate ML model (chính xác)
4. Test và so sánh kết quả

