# 🤖 Setup GPT Text Correction Fallback

## 🎯 Tổng quan

Hệ thống tự động fallback: **ProtonX (local)** → **GPT-4o-mini (API)** → **None**

Nếu ProtonX không chạy được (torch error), sẽ tự động dùng GPT API để chỉnh sửa văn bản tiếng Việt.

## 📦 Cài đặt

### 1. Cài OpenAI package

```bash
cd ocr-service-python
pip install openai
```

### 2. Lấy OpenAI API Key

1. Đăng ký/đăng nhập: https://platform.openai.com
2. Vào: https://platform.openai.com/api-keys
3. Tạo API key mới
4. Copy key (format: `sk-...`)

### 3. Set API Key

**Option 1: Environment variable (Khuyên dùng)**

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="sk-your-api-key-here"

# Windows CMD
set OPENAI_API_KEY=sk-your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=sk-your-api-key-here
```

**Option 2: .env file**

1. Copy `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```

2. Sửa `.env`:
   ```env
   OPENAI_API_KEY=sk-your-api-key-here
   ```

**Option 3: Request parameter (optional)**

Có thể truyền qua API:
```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.pdf" \
  -F "openaiApiKey=sk-your-api-key-here"
```

## 🚀 Test

### 1. Chạy service

```bash
python app.py
```

Bạn sẽ thấy:
- ✅ Nếu ProtonX available: "✅ ProtonX Text Correction sẵn sàng"
- ✅ Nếu không có ProtonX nhưng có GPT: "✅ GPT-4o-mini Text Correction sẵn sàng"

### 2. Test API

```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.pdf"
```

### 3. Check health

```bash
curl http://localhost:5001/health
```

Response sẽ cho biết method đang dùng:
```json
{
  "text_correction": {
    "available": true,
    "method": "gpt",
    "model": "GPT-4o-mini"
  }
}
```

## 💰 Chi phí

GPT-4o-mini rất rẻ:
- **$0.15 per 1M input tokens**
- **$0.60 per 1M output tokens**

Ví dụ:
- 1000 từ tiếng Việt ≈ ~2000 tokens
- Cost: ~$0.0003-0.0012 per 1000 từ
- **1 triệu từ ≈ ~$0.30-1.20**

## 📝 Prompt Design

GPT được prompt chuyên biệt để:
- ✅ Chỉ sửa chính tả
- ✅ Không thêm bớt nội dung
- ✅ Không paraphrase
- ✅ Giữ nguyên ý nghĩa

## ✅ Lợi ích

- ✅ **Auto fallback** - Không cần config
- ✅ **Reliable** - Luôn có text correction
- ✅ **Accurate** - GPT-4o-mini rất tốt
- ✅ **Cheap** - Chi phí rất thấp

