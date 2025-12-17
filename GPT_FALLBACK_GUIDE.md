# 🤖 GPT Text Correction Fallback

## ✨ Giới thiệu

Nếu ProtonX model không chạy được (torch DLL error, etc.), hệ thống sẽ **tự động fallback** sang **GPT-4o-mini API** để chỉnh sửa văn bản tiếng Việt.

## 🔄 Auto Fallback Flow

```
PaddleOCR → Raw Text
    ↓
Thử ProtonX (local, free)
    ↓ (nếu fail)
Thử GPT-4o-mini (API, cần key)
    ↓ (nếu fail)
Trả về text gốc (không correct)
```

## 📦 Cài đặt

### 1. Cài OpenAI package

```bash
pip install openai
```

Hoặc cài tất cả:
```bash
pip install -r requirements.txt
```

### 2. Set OpenAI API Key

**Option 1: Environment variable (Khuyên dùng)**

```bash
# Windows
set OPENAI_API_KEY=sk-your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=sk-your-api-key-here
```

**Option 2: .env file**

Tạo file `.env` trong `ocr-service-python/`:

```env
OPENAI_API_KEY=sk-your-api-key-here
```

**Option 3: Request parameter**

Có thể truyền qua API request (optional):

```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.pdf" \
  -F "openaiApiKey=sk-your-api-key-here"
```

## 🎯 Cách hoạt động

### 1. ProtonX Available (Priority 1)

Nếu ProtonX chạy được, sẽ dùng ProtonX (local, free):

```
🔧 Sử dụng ProtonX Text Correction (local)...
```

### 2. GPT Fallback (Priority 2)

Nếu ProtonX không available, tự động dùng GPT:

```
⚠️  ProtonX không khả dụng
🔧 Fallback sang GPT-4o-mini Text Correction (API)...
```

### 3. No Correction (Priority 3)

Nếu cả 2 đều không available, trả về text gốc:

```
⚠️  Không có text correction nào khả dụng. Trả về text gốc.
```

## 🚀 Sử dụng

Service sẽ tự động chọn method tốt nhất. Không cần config gì thêm!

### API Call

```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@document.pdf" \
  -F "useTextCorrection=true"
```

### Response

```json
{
  "success": true,
  "text": "Văn bản đã được sửa chính tả...",
  "text_correction": true,
  "method": "ocr",
  ...
}
```

## 📝 GPT Prompt

GPT được prompt chuyên biệt để:
- ✅ **Chỉ sửa chính tả** (dấu, từ sai)
- ✅ **Sửa lỗi ngắt từ**
- ✅ **Chuẩn hóa dấu câu**
- ❌ **KHÔNG thêm, bớt, hoặc thay đổi nội dung**
- ❌ **KHÔNG paraphrase hay viết lại**

### Prompt Template

```
Bạn là chuyên gia chỉnh sửa văn bản tiếng Việt. 
Nhiệm vụ: Sửa chính tả và chuẩn hóa văn bản SAU KHI OCR, 
nhưng KHÔNG được thêm bớt hoặc thay đổi nội dung.

YÊU CẦU:
1. Chỉ sửa lỗi chính tả (dấu, từ sai)
2. Sửa lỗi ngắt từ
3. Chuẩn hóa dấu câu
4. KHÔNG được thêm, bớt, hoặc thay đổi nội dung
5. KHÔNG được paraphrase hay viết lại
6. Giữ nguyên ý nghĩa và cấu trúc câu
```

## 💰 Chi phí

- **ProtonX**: Miễn phí (local)
- **GPT-4o-mini**: ~$0.15-0.60 per 1M tokens (rất rẻ)
  - 1000 từ tiếng Việt ≈ ~2000 tokens
  - Cost: ~$0.0003-0.0012 per 1000 từ

## ✅ Ưu điểm

- ✅ **Auto fallback** - Tự động chọn method tốt nhất
- ✅ **Không gián đoạn** - Service vẫn chạy nếu ProtonX fail
- ✅ **Chính xác cao** - GPT-4o-mini rất tốt với tiếng Việt
- ✅ **Không thêm bớt** - Prompt được thiết kế chuyên biệt

## 🔍 Kiểm tra Status

### Health Check

```bash
curl http://localhost:5001/health
```

Response:
```json
{
  "text_correction": {
    "available": true,
    "method": "gpt",  // hoặc "protonx"
    "model": "GPT-4o-mini",
    "description": "..."
  }
}
```

## 🆘 Troubleshooting

### GPT API không hoạt động

**Lỗi**: "GPT API không khả dụng"

**Giải pháp**:
1. Kiểm tra API key: `echo $OPENAI_API_KEY`
2. Kiểm tra key có đúng format: `sk-...`
3. Kiểm tra có đủ credit trong OpenAI account

### Muốn force dùng GPT

Hiện tại system tự động chọn. Nếu muốn force GPT (bỏ ProtonX), có thể:
- Tắt ProtonX: Set `TORCH_AVAILABLE = False`
- Hoặc không cài torch

### Muốn force dùng ProtonX

- Không set `OPENAI_API_KEY`
- Hoặc xóa GPT fallback code

## 📊 So sánh

| Feature | ProtonX | GPT-4o-mini |
|---------|---------|-------------|
| Cost | Free | $0.15-0.60/1M tokens |
| Speed | Medium | Fast |
| Accuracy | 90-95% | 95-98% |
| Setup | Cần torch | Cần API key |
| Location | Local | API |

## 🎯 Recommendation

- **Development**: Dùng ProtonX (free)
- **Production**: Dùng GPT fallback (reliable hơn)
- **Best**: Auto fallback (system tự chọn)

