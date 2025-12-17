# Giải Pháp Sửa Chính Tả Tiếng Việt Chuyên Nghiệp

## Vấn đề
Cần một mô hình chuyên sửa lỗi chính tả tiếng Việt cho văn bản OCR, đặc biệt là văn bản chuyên ngành (pháp lý, hành chính).

## Giải pháp đã tạo: `vietnamese_spell_correction_comprehensive.py`

### Multi-layer Approach

```
OCR Output (PaddleOCR)
    ↓
Layer 1: Rule-based Correction (Nhanh, fix lỗi dễ)
    - Dictionary lớn với 100+ từ thường gặp
    - Rules cho dấu thanh điệu
    - Rules cho dấu câu
    - Aggressive mode: Sửa nhiều pattern hơn
    ↓
Layer 2: ML Model hoặc GPT (Chính xác, fix lỗi phức tạp)
    - ProtonX model (nếu available)
    - GPT-4o-mini (nếu có API key)
    ↓
Final Corrected Text ✅
```

### Features

1. **Comprehensive Dictionary**
   - 100+ từ thường gặp trong văn bản pháp lý, hành chính
   - Từ chức danh: giám đốc, viện trưởng, chủ tịch...
   - Từ địa danh: thành phố, tỉnh, huyện, xã...
   - Động từ: thực hiện, kiểm tra, xác nhận...

2. **Auto Method Selection**
   - Tự động chọn method tốt nhất available
   - GPT → ProtonX → Rule-based

3. **Aggressive Mode**
   - Sửa nhiều pattern hơn
   - Tốt cho văn bản có nhiều lỗi

## Cách sử dụng

### 1. Basic Usage

```python
from vietnamese_spell_correction_comprehensive import correct_vietnamese_spelling

# Auto: Tự chọn method tốt nhất
corrected = correct_vietnamese_spelling(text, method="auto", aggressive=True)
```

### 2. Specify Method

```python
# Chỉ dùng rule-based (nhanh)
corrected = correct_vietnamese_spelling(text, method="rule")

# Dùng ProtonX model
corrected = correct_vietnamese_spelling(text, method="protonx")

# Dùng GPT-4o-mini
corrected = correct_vietnamese_spelling(text, method="gpt")
```

### 3. Integrated vào app.py

Đã cập nhật `text_correction_wrapper.py` để dùng system mới:

```python
from text_correction_wrapper import correct_vietnamese_text

# Tự động dùng comprehensive correction
corrected = correct_vietnamese_text(ocr_output, use_correction=True)
```

## So sánh các phương pháp

| Method | Tốc độ | Độ chính xác | Chi phí | Phù hợp cho |
|--------|--------|--------------|---------|-------------|
| Rule-based | ⚡⚡⚡ Rất nhanh | ⭐⭐ Trung bình | Free | Văn bản có ít lỗi |
| Rule + ProtonX | ⚡⚡ Chậm | ⭐⭐⭐ Tốt | Free | Văn bản pháp lý |
| Rule + GPT | ⚡⚡ Chậm | ⭐⭐⭐⭐ Rất tốt | ~$0.01/1K tokens | Văn bản phức tạp |

## Các mô hình có thể thêm sau

### 1. PhoBERT fine-tuned
- Model: `vinai/phobert-base`
- Fine-tune cho text correction
- Tốt nhất nhưng cần data và thời gian

### 2. Các model trên Hugging Face
- Search: "vietnamese text correction"
- Test và so sánh

### 3. Custom Dictionary
- Mở rộng dictionary với từ chuyên ngành
- Rules cho pattern cụ thể

## Recommendation

**Dùng giải pháp hiện tại với GPT-4o-mini** (nếu có API key):

- ✅ Rule-based layer fix nhanh các lỗi dễ
- ✅ GPT-4o-mini fix chính xác các lỗi phức tạp
- ✅ Hiểu context tốt
- ✅ Tốt cho văn bản chuyên ngành

**Nếu không có API key**:

- ✅ Rule-based với dictionary lớn
- ✅ Có thể thêm ProtonX (nếu load được)

## Next Steps

1. ✅ Đã tạo comprehensive solution
2. ✅ Đã tích hợp vào text_correction_wrapper
3. ⏳ Test với văn bản thực tế
4. ⏳ Mở rộng dictionary nếu cần
5. ⏳ Tìm thêm models trên Hugging Face

## Test

```bash
cd ocr-service-python
python -c "from vietnamese_spell_correction_comprehensive import correct_vietnamese_spelling; print(correct_vietnamese_spelling('toi khong co gi de noi', method='auto'))"
```

Kết quả mong đợi: `tôi không có gì để nói`

