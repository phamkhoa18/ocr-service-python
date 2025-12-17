# Flow: PaddleOCR → ProtonX → Trả về

## Flow đơn giản

```
PaddleOCR (lấy text từ ảnh/PDF)
    ↓
ProtonX Legal Text Correction Model (sửa chính tả tiếng Việt)
    ↓
Trả về text đã sửa chính tả ✅
```

## Files đã cập nhật

### 1. `text_correction_wrapper.py`
- Chỉ dùng ProtonX model
- Loại bỏ GPT và các method phức tạp khác
- Flow: PaddleOCR text → ProtonX → Corrected text

### 2. `app.py`
- Cập nhật để check ProtonX availability
- Sử dụng ProtonX thay vì GPT

### 3. `text_correction.py`
- Đã có sẵn ProtonX implementation
- Model: `protonx-models/protonx-legal-tc`

## Cách hoạt động

1. **PaddleOCR** nhận dạng text từ ảnh/PDF
2. **ProtonX model** sửa chính tả tiếng Việt:
   - Sửa dấu thanh điệu
   - Sửa từ sai
   - Sửa ngắt từ
   - Giữ nguyên nội dung và layout
3. **Trả về** text đã sửa chính tả

## Dependencies cần có

```bash
# OCR
paddleocr==2.7.3
paddlepaddle==2.6.2

# Text Correction (ProtonX)
transformers>=4.30.0
torch>=2.0.0
sentencepiece>=0.1.99
accelerate>=0.20.0
```

## Cài đặt

```bash
cd ocr-service-python
pip install -r requirements.txt
```

## Lưu ý

1. **Lần đầu sử dụng**: Model sẽ tự động download từ Hugging Face (~500MB-1GB)
   - Cần internet để download
   - Cần ~1GB disk space

2. **Lazy loading**: Model chỉ load khi sử dụng lần đầu tiên

3. **GPU support**: Có thể dùng GPU nếu có CUDA (nhanh hơn)

## Test

Chạy OCR service và test với file ảnh/PDF:

1. Upload file qua API
2. PaddleOCR sẽ extract text
3. ProtonX sẽ sửa chính tả
4. Nhận kết quả text đã sửa

## Troubleshooting

### Lỗi: Model không load được
- Kiểm tra internet (cần để download model)
- Kiểm tra disk space (~1GB)
- Kiểm tra transformers, torch đã cài đặt chưa

### Lỗi: Torch DLL error (Windows)
- Cài Visual C++ Redistributable
- Hoặc: `pip uninstall torch && pip install torch`

### Model quá chậm
- Thử dùng GPU: `use_gpu=True`
- Hoặc giảm text length trước khi gửi cho ProtonX

## Example

```python
# Trong app.py
text = "can cu bo luat lao dong 2019"  # Text từ PaddleOCR

# Gọi ProtonX để sửa
corrected = correct_vietnamese_text(text, use_correction=True)
# Kết quả: "căn cứ bộ luật lao động 2019"
```

