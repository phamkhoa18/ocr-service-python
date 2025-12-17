# ⚡ Quick Start - Python OCR Service

## 🚀 Cài đặt nhanh

### 1. Cài đặt Python dependencies
```bash
cd ocr-service-python
pip install -r requirements.txt
```

### 2. Cài đặt Poppler (Windows)
- Download: https://github.com/oschwartz10612/poppler-windows/releases
- Giải nén và thêm `bin` folder vào PATH

### 3. Chạy service
```bash
python app.py
```

Service sẽ chạy tại: `http://localhost:5001`

## 📡 Test API

### Health check
```bash
curl http://localhost:5001/health
```

### Extract text từ ảnh
```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.jpg"
```

### Extract text từ PDF
```bash
curl -X POST http://localhost:5001/extract-text \
  -F "file=@test.pdf"
```

## 🔗 Tích hợp với Frontend

Cập nhật `ocrService.ts` để gọi Python API trực tiếp:

```typescript
const PYTHON_OCR_URL = 'http://localhost:5001';

async extractText(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${PYTHON_OCR_URL}/extract-text`, {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
}
```

## ✅ Xong!

Service sẽ tự động download PaddleOCR models lần đầu (mất vài phút). Models được cache sau đó.

