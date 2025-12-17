# ✅ Flow cuối cùng: PaddleOCR → GPT-4o-mini

## 🎯 Pipeline

```
┌──────────────────────┐
│  Upload PDF/Image    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   PaddleOCR          │ → Lấy text thô (có thể sai chính tả)
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   GPT-4o-mini        │ → Gọi ChatGPT API để chỉnh sửa chính tả
│   (ChatGPT)          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   Text chuẩn         │ → Đã được sửa chính tả, không thêm bớt
└──────────────────────┘
```

## ✅ Xác nhận

- ✅ **Bỏ ProtonX** - Không dùng nữa
- ✅ **Chỉ dùng GPT-4o-mini** - Gọi ChatGPT API
- ✅ **Sau OCR** → Luôn gọi ChatGPT
- ✅ **Prompt nghiêm ngặt** - Chỉ sửa chính tả, không thêm bớt

## 📝 Code Flow

### 1. OCR với PaddleOCR
```python
# PaddleOCR lấy text thô
raw_text = ocr_image(image)  # Text có thể sai chính tả
```

### 2. Gọi ChatGPT để sửa chính tả
```python
# Gọi GPT-4o-mini
corrected_text = correct_vietnamese_text(raw_text)  
# → Gọi OpenAI API với model="gpt-4o-mini"
```

### 3. Return text chuẩn
```python
return {
    'text': corrected_text,  # Đã được sửa chính tả
    ...
}
```

## 🔧 Setup

1. Set `OPENAI_API_KEY`:
   ```bash
   set OPENAI_API_KEY=sk-your-key-here
   ```

2. Chạy service:
   ```bash
   python app.py
   ```

3. Upload file → Tự động gọi ChatGPT để sửa chính tả!

## ✅ Done!

System đã được cấu hình để:
- ✅ PaddleOCR lấy text
- ✅ GPT-4o-mini (ChatGPT) chỉnh sửa chính tả
- ✅ Không thêm bớt nội dung
- ✅ Text chuẩn tiếng Việt

