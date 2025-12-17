# VIETOCR Integration Guide

## VIETOCR là gì?

VIETOCR là một OCR engine chuyên dụng cho tiếng Việt, được phát triển bởi pbcquoc:
- GitHub: https://github.com/pbcquoc/vietocr
- Chuyên nhận dạng tiếng Việt (cả in và viết tay)
- Có thể cho kết quả tốt hơn PaddleOCR cho một số trường hợp

**Lưu ý**: VIETOCR là OCR engine, KHÔNG phải text correction model. Nó vẫn có thể có lỗi chính tả và cần post-processing.

## Giải pháp đề xuất

### Option 1: Dùng VIETOCR thay PaddleOCR
- Thay thế PaddleOCR bằng VIETOCR
- Kết hợp với text correction model sau OCR

### Option 2: Dùng PaddleOCR + Text Correction Model tốt hơn
- Giữ PaddleOCR (đã ổn định)
- Tìm và tích hợp text correction model tốt hơn

### Option 3: Kết hợp cả hai
- Cho phép chọn OCR engine (PaddleOCR hoặc VIETOCR)
- Dùng text correction model tốt nhất

## Các mô hình Text Correction tiếng Việt

1. **PhoBERT-based models**: Mô hình BERT cho tiếng Việt
2. **Sequence-to-sequence models**: Mô hình dịch máy để sửa lỗi
3. **Rule-based + ML hybrid**: Kết hợp rules và ML

## Next Steps

Tôi sẽ tạo integration cho các options trên.

