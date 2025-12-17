# 🔗 Hướng dẫn Tích hợp Python OCR Service

## 📋 Tổng quan

Python OCR Service là backend riêng chuyên xử lý OCR tiếng Việt với **PaddleOCR** - thư viện OCR tốt nhất cho tiếng Việt.

## 🚀 Setup

### 1. Cài đặt Python Service

```bash
cd ocr-service-python

# Tạo virtual environment (khuyên dùng)
python -m venv venv

# Kích hoạt venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài dependencies
pip install -r requirements.txt
```

### 2. Cài đặt Poppler (cho PDF)

**Windows:**
- Download: https://github.com/oschwartz10612/poppler-windows/releases
- Giải nén và thêm vào PATH
- Hoặc: `choco install poppler`

**Kiểm tra:**
```bash
pdftoppm -h
```

### 3. Chạy Python Service

```bash
python app.py
```

Service sẽ chạy tại: `http://localhost:5001`

## 🔧 Tích hợp với Node.js Backend

### Option 1: Forward request từ Node.js (Khuyên dùng)

1. **Cài thêm dependencies:**
```bash
cd backend-app
npm install form-data
```

2. **Cập nhật `.env` của Node.js:**
```env
PYTHON_OCR_URL=http://localhost:5001
USE_PYTHON_OCR=true  # Optional: tự động dùng Python OCR
```

3. **Cập nhật OCRRouter để hỗ trợ cả 2:**
   - `/api/v1/ocr/extract-text` - Node.js OCR (hiện tại)
   - `/api/v1/ocr/extract-text-python` - Python OCR (mới)

### Option 2: Frontend gọi trực tiếp Python API

Cập nhật `ocrService.ts` để gọi Python API:

```typescript
const PYTHON_OCR_URL = import.meta.env.VITE_PYTHON_OCR_URL || 'http://localhost:5001';

async extractTextFromPython(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${PYTHON_OCR_URL}/extract-text`, {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
}
```

## 📡 API Endpoints

### Python Service

- `GET /health` - Health check
- `POST /extract-text` - Extract text từ PDF/Image

### Node.js Proxy

- `GET /api/v1/ocr/python-health` - Check Python service
- `POST /api/v1/ocr/extract-text-python` - Forward tới Python

## ✅ Ưu điểm Python OCR

- ✅ **PaddleOCR** - Tốt nhất cho tiếng Việt
- ✅ Không cần canvas - Xử lý PDF bằng PyMuPDF
- ✅ Không cần worker setup phức tạp
- ✅ Image preprocessing tốt hơn với OpenCV
- ✅ Hỗ trợ cả PDF có text và PDF scan

## 🆚 So sánh

| Tính năng | Node.js OCR | Python OCR |
|-----------|-------------|------------|
| Tiếng Việt | Tốt (Tesseract) | Rất tốt (PaddleOCR) |
| PDF scan | Cần canvas | ✅ Sẵn sàng |
| Setup | Phức tạp | Đơn giản |
| Tốc độ | Nhanh | Rất nhanh |
| Độ chính xác | 85-90% | 90-95% |

## 💡 Recommendation

**Sử dụng Python OCR cho:**
- PDF scan (đã quét)
- Văn bản tiếng Việt phức tạp
- Yêu cầu độ chính xác cao

**Giữ Node.js OCR cho:**
- Ảnh đơn giản
- PDF có text layer
- Cần tốc độ nhanh

