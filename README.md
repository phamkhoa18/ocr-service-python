# OCR Service Python Backend

Backend Python chuyên xử lý OCR tiếng Việt sử dụng **PaddleOCR** - thư viện OCR tốt nhất cho tiếng Việt.

## ✨ Tính năng

- ✅ **OCR tiếng Việt chuyên nghiệp** với PaddleOCR
- ✅ **Text Correction tự động** với ProtonX Legal Text Correction v1.3 (chuẩn hóa tiếng Việt)
- ✅ Hỗ trợ **PDF có text layer** và **PDF scan** (đã quét)
- ✅ Hỗ trợ nhiều định dạng ảnh: PNG, JPG, JPEG, GIF, BMP, WEBP, TIFF
- ✅ **Image preprocessing** tối ưu cho tiếng Việt
- ✅ Tự động detect PDF có text vs PDF scan
- ✅ Xử lý PDF nhiều trang
- ✅ API đơn giản, dễ tích hợp

### 🎯 Pipeline xử lý

```
PDF/Image → PaddleOCR → Raw Text → ProtonX Correction → Final Text (chuẩn tiếng Việt)
```

## 📦 Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Cài đặt Poppler (cho PDF processing)

**Windows:**
- Tải từ: https://github.com/oschwartz10612/poppler-windows/releases
- Giải nén và thêm vào PATH
- Hoặc dùng Chocolatey: `choco install poppler`

**Linux:**
```bash
sudo apt-get install poppler-utils
```

**Mac:**
```bash
brew install poppler
```

### 3. Cấu hình môi trường

Tạo file `.env` trong thư mục `ocr-service-python` với nội dung:
```env
# Text Correction API URL (mặc định: http://localhost:5001/correct)
TEXT_CORRECTION_API_URL=http://localhost:5001/correct

# OCR Service Port (mặc định: 4000)
PORT=4000

# OpenAI API Key (nếu sử dụng GPT text correction)
OPENAI_API_KEY=your-openai-api-key-here
```

**Lưu ý**: File `.env` đã được thêm vào `.gitignore` để bảo mật cấu hình của bạn.

## 🚀 Chạy Service

```bash
python app.py
```

Service sẽ chạy trên port được cấu hình trong `.env` (mặc định: `http://localhost:4000`)

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```

### 2. Extract Text
```
POST /extract-text
Content-Type: multipart/form-data

FormData:
  - file: PDF hoặc Image (required)
  - forceOCR: 'true' (optional) - Force OCR ngay cả khi PDF có text
```

**Response:**
```json
{
  "success": true,
  "text": "Văn bản đã trích xuất...",
  "pages": 1,
  "confidence": 95.5,
  "method": "ocr",
  "processing_time": "2.34s",
  "text_length": 1500,
  "word_count": 250
}
```

## 🔧 Tích hợp với Node.js Backend

Cập nhật Node.js backend để gọi Python API:

1. Set `PYTHON_OCR_URL` trong `.env` của Node.js backend
2. Cập nhật `ocrService.ts` để call Python API

## 📝 Notes

- PaddleOCR tự động download models lần đầu chạy (có thể mất vài phút)
- Models sẽ được cache, lần sau sẽ nhanh hơn
- Nếu có GPU, set `USE_GPU=true` trong `.env` để tăng tốc độ

## 🆘 Troubleshooting

### Lỗi: Module not found
```bash
pip install -r requirements.txt
```

### Lỗi: Poppler not found
Cài đặt Poppler và thêm vào PATH

### Models download chậm
Models sẽ được cache sau lần download đầu tiên

