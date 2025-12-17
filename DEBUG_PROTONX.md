# Debug: ProtonX Model Loading

## Vấn đề
Model ProtonX không sửa chính tả, có thể do:
1. Model không được load
2. Model load nhưng không được gọi
3. Model load nhưng lỗi khi sử dụng
4. Model trả về text gốc (không sửa)

## Đã thêm logging chi tiết

### 1. Model initialization logging
- Log khi bắt đầu tải model
- Log khi tải tokenizer
- Log khi tải model
- Log khi chuyển model sang device
- Log lỗi chi tiết nếu có

### 2. Text correction logging
- Log input text
- Log số câu đã tách
- Log từng câu đang sửa
- Log kết quả sau khi sửa
- Log output text

### 3. Error logging
- Full traceback khi có lỗi
- Chi tiết lỗi từng bước

## Cách check

### 1. Chạy OCR và xem logs
```
→ Đang lấy corrector instance...
→ Corrector instance: <...>
→ Model initialized: True/False
```

### 2. Check model load
Nếu thấy:
```
🔄 Đang tải ProtonX Text Correction model...
   Model: protonx-models/protonx-legal-tc
   → Đang tải tokenizer...
   ✅ Tokenizer đã tải xong
   → Đang tải model...
   ✅ Model đã tải xong
   ✅ ProtonX Text Correction model đã sẵn sàng!
```
→ Model đã load thành công

### 3. Check text correction
Nếu thấy:
```
🔧 BẮT ĐẦU SỬA CHÍNH TẢ TIẾNG VIỆT
📝 Input: ...
→ Đang lấy corrector instance...
→ Model initialized: True
→ Text ngắn, dùng correct_text...
📝 Đã tách thành X câu
   → Đang sửa câu 1/X: ...
      ✅ Đã sửa: ...
✅ HOÀN THÀNH SỬA CHÍNH TẢ
📝 Output: ...
```
→ Đang sửa chính tả

## Troubleshooting

### Model không load
- Check internet (cần để download)
- Check disk space (~1GB)
- Check transformers, torch đã cài chưa
- Xem error logs

### Model load nhưng không sửa
- Check logs xem có gọi correct_text không
- Check input/output có khác nhau không
- Test với text có lỗi rõ ràng: "toi khong co gi"

### Model trả về text gốc
- Có thể model không sửa được (quá tốt hoặc quá kém)
- Test với text có lỗi: "can cu bo luat" → "căn cứ bộ luật"

