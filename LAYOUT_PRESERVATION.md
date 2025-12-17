# 📐 Layout Preservation - Giữ nguyên layout khi OCR

## 🎯 Giải pháp

System đã được cải thiện để **giữ nguyên layout** (bảng, cột, spacing, alignment) khi OCR và sửa chính tả.

## 🔧 Cách hoạt động

### 1. OCR với Layout Detection

PaddleOCR trả về **bounding boxes** cho mỗi dòng text. System sử dụng thông tin này để:

- ✅ **Detect tables** - Phát hiện cấu trúc bảng từ spacing
- ✅ **Preserve columns** - Giữ nguyên cột bằng tabs/spacing
- ✅ **Maintain alignment** - Giữ căn chỉnh và indentation
- ✅ **Keep line breaks** - Giữ nguyên dòng trống, paragraph breaks

### 2. Format Text với Layout Markers

- **Tables** → Sử dụng tabs (`\t`) để phân cách cột
- **Lists** → Giữ nguyên số/bullet format
- **Spacing** → Giữ nguyên multiple spaces để alignment
- **Indentation** → Giữ leading spaces

### 3. GPT với Layout-Aware Prompt

Prompt được cải thiện để GPT:
- ✅ Giữ nguyên layout khi sửa chính tả
- ✅ Không thay đổi spacing, columns, tables
- ✅ Chỉ sửa chính tả, không reformat

## 📊 Ví dụ

### Input (OCR raw):
```
STT  Ten      Tuoi    Dia chi
1    Nguyen   25      Ha Noi
2    Tran     30      Ho Chi Minh
```

### Output (Sau GPT correction):
```
STT  Tên      Tuổi    Địa chỉ
1    Nguyễn   25      Hà Nội
2    Trần     30      Hồ Chí Minh
```

✅ **Layout được giữ nguyên!**

## ✅ Tính năng

- ✅ **Table detection** - Tự động detect bảng từ spacing
- ✅ **Column preservation** - Giữ nguyên cột bằng tabs
- ✅ **Spacing preservation** - Giữ alignment và indentation
- ✅ **GPT layout-aware** - Prompt đặc biệt để giữ layout

## 🎯 Kết quả

- ✅ Layout được giữ nguyên
- ✅ Chính tả được sửa chuẩn
- ✅ Bảng, cột, spacing được preserve
- ✅ Dễ đọc và sử dụng

