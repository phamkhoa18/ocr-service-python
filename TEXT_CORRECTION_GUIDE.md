# 📝 Hướng dẫn Text Correction - ProtonX Legal TC

## ✨ Giới thiệu

OCR Service đã được tích hợp **ProtonX Legal Text Correction v1.3** - mô hình chuyên chỉnh sửa văn bản tiếng Việt, đặc biệt tối ưu cho output của PaddleOCR và các công cụ OCR khác.

## 🎯 Tính năng

Model này tự động sửa các lỗi OCR phổ biến:

- ✅ **Missing/incorrect diacritics** - Sửa dấu tiếng Việt (ă, â, ê, ô, ơ, ư, đ, etc.)
- ✅ **Broken word segmentation** - Sửa lỗi ngắt từ
- ✅ **Misrecognized legal terms** - Sửa thuật ngữ pháp lý
- ✅ **Punctuation artifacts** - Sửa dấu câu
- ✅ **Formatting inconsistencies** - Chuẩn hóa định dạng

## 🔗 Model Info

- **Model**: `protonx-models/protonx-legal-tc`
- **Version**: v1.3
- **Type**: Seq2Seq Transformer
- **Hugging Face**: https://huggingface.co/protonx-models/protonx-legal-tc
- **Max sequence length**: 128 tokens

## 📦 Cài đặt

### 1. Dependencies

Model sẽ tự động download khi chạy lần đầu. Cần cài các dependencies:

```bash
pip install transformers torch sentencepiece accelerate
```

Hoặc cài tất cả:
```bash
pip install -r requirements.txt
```

### 2. Model Download

Model sẽ tự động download từ Hugging Face khi chạy lần đầu (có thể mất vài phút). Model sẽ được cache cho lần sau.

**Lưu ý**: Cần kết nối internet để download model lần đầu.

## 🚀 Sử dụng

### Mặc định

Text correction được **bật mặc định** cho tất cả OCR requests.

```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.pdf"
```

### Tắt Text Correction

Nếu muốn tắt text correction:

```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.pdf" \
  -F "useTextCorrection=false"
```

## 📊 Ví dụ

### Trước khi correction (PaddleOCR output):
```
Cǎn cú Hién pháp nuóc Cōng hòa xā hi chù nghia Viēt Nam;
```

### Sau khi correction (ProtonX output):
```
Căn cứ Hiến pháp nước Cộng hòa xã hội chủ nghĩa Việt Nam;
```

## ⚙️ Configuration

### Environment Variables

Trong `.env`:

```env
USE_TEXT_CORRECTION=true  # Enable/disable text correction (default: true)
USE_GPU=false  # Use GPU for text correction (faster if available)
```

### Code

```python
from text_correction import correct_vietnamese_text

# Enable correction
corrected_text = correct_vietnamese_text(text, use_correction=True)

# Disable correction
original_text = correct_vietnamese_text(text, use_correction=False)
```

## 🔧 Tích hợp vào Pipeline

Text correction được tự động tích hợp vào pipeline:

1. **OCR với PaddleOCR** → Raw text
2. **Text Correction với ProtonX** → Corrected text (chuẩn tiếng Việt)

### Flow

```
PDF/Image → PaddleOCR → Raw OCR Text → ProtonX Correction → Final Text
```

## 📈 Performance

- **Accuracy**: Rất cao cho văn bản pháp lý và văn bản chính thức
- **Speed**: 
  - CPU: ~0.5-2s per sentence
  - GPU: ~0.1-0.5s per sentence
- **Memory**: ~500MB-1GB (model size)

## 🎯 Use Cases

- ✅ OCR post-processing
- ✅ Legal document normalization
- ✅ Government document standardization
- ✅ Contract proofreading
- ✅ Administrative workflow automation

## ⚠️ Limitations

- Không paraphrase hoặc rewrite văn bản
- Không thể khôi phục nội dung bị thiếu
- Tối ưu cho tiếng Việt (không phải tiếng Anh hoặc ngôn ngữ khác)
- Không phù hợp cho social media slang

## 🆘 Troubleshooting

### Model không download được

**Lỗi**: `ConnectionError` khi download model

**Giải pháp**:
1. Kiểm tra kết nối internet
2. Model sẽ được download khi chạy lần đầu
3. Có thể download manual từ Hugging Face

### Text correction chậm

**Nguyên nhân**: Đang chạy trên CPU

**Giải pháp**:
1. Nếu có GPU, set `USE_GPU=true` trong `.env`
2. Text correction sẽ nhanh hơn đáng kể với GPU

### Memory error

**Nguyên nhân**: Model quá lớn cho RAM

**Giải pháp**:
1. Model cần ~1GB RAM
2. Đảm bảo có đủ RAM trống
3. Có thể tắt text correction nếu cần: `useTextCorrection=false`

## 📝 Notes

- Text correction được khuyến nghị cho tất cả OCR output
- Đặc biệt quan trọng cho văn bản pháp lý
- Model được train trên 70,000+ correction pairs
- Đảm bảo không thay đổi ý nghĩa văn bản (strict constraints)

