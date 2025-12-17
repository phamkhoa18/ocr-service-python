# ✅ Setup: Chỉ dùng GPT-4o-mini (Bỏ ProtonX)

## 🎯 Thay đổi

**Đã bỏ ProtonX, chỉ dùng GPT-4o-mini để chỉnh sửa chính tả.**

Pipeline mới:
```
PaddleOCR → Raw Text
    ↓
GPT-4o-mini (ChatGPT) → Corrected Text (chuẩn tiếng Việt)
```

## 📋 Setup

### 1. Cài OpenAI package

```bash
cd ocr-service-python
pip install openai
```

### 2. Set OpenAI API Key

**Windows:**
```bash
set OPENAI_API_KEY=sk-your-api-key-here
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY=sk-your-api-key-here
```

**Hoặc tạo file `.env`:**
```env
OPENAI_API_KEY=sk-your-api-key-here
```

### 3. Chạy service

```bash
python app.py
```

Bạn sẽ thấy:
```
✅ GPT-4o-mini Text Correction sẵn sàng (ChatGPT API)
📝 Sẽ gọi ChatGPT sau khi PaddleOCR lấy text để chỉnh sửa chính tả
```

## 🔄 Flow hoạt động

1. **Upload PDF/Image** → PaddleOCR lấy text thô
2. **Gọi ChatGPT (GPT-4o-mini)** → Chỉnh sửa chính tả tiếng Việt
3. **Return text chuẩn** → Đã được sửa chính tả

## ✅ Xác nhận

- ✅ **Bỏ ProtonX** - Không dùng nữa
- ✅ **Chỉ dùng GPT-4o-mini** - Gọi ChatGPT API
- ✅ **Sau OCR** → Luôn gọi ChatGPT để sửa chính tả
- ✅ **Prompt nghiêm ngặt** - Chỉ sửa chính tả, không thêm bớt

## 🆘 Nếu thiếu API Key

Service vẫn chạy nhưng sẽ không có text correction:
```
⚠️  GPT-4o-mini Text Correction chưa sẵn sàng: Thiếu OPENAI_API_KEY
⚠️  OCR vẫn hoạt động bình thường, nhưng sẽ không có text correction.
```

Set API key để enable text correction!

