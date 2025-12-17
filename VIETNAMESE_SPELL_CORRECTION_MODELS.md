# Các Mô Hình Sửa Chính Tả Tiếng Việt

## Vấn đề
Cần một mô hình chuyên sửa lỗi chính tả tiếng Việt, đặc biệt cho văn bản chuyên ngành.

## Các mô hình có sẵn

### 1. ProtonX Legal Text Correction
- **Model**: `protonx-models/protonx-legal-tc`
- **Chuyên**: Văn bản pháp lý
- **Type**: Sequence-to-sequence
- **Status**: Đã tích hợp nhưng gặp vấn đề load

### 2. PhoBERT-based Models
- **Models**: `vinai/phobert-base`, `vinai/phobert-large`
- **Type**: BERT cho tiếng Việt
- **Cần**: Fine-tune cho text correction
- **Pros**: Tốt cho context understanding
- **Cons**: Cần fine-tune

### 3. GPT-4o-mini (OpenAI)
- **Type**: LLM API
- **Pros**: Rất tốt, hiểu context
- **Cons**: Cần API key, có chi phí

### 4. Rule-based + Dictionary
- **Libraries**: pyenchant, pyspellchecker (nhưng không support Vietnamese)
- **Custom**: Tự build dictionary và rules
- **Pros**: Nhanh, free
- **Cons**: Không chính xác bằng ML

### 5. Các mô hình khác cần tìm
- Tìm trên Hugging Face với keyword: "vietnamese text correction"
- Tìm các research papers về Vietnamese spell correction
- Tìm các repo GitHub về Vietnamese NLP

## Giải pháp đề xuất

### Option 1: Fine-tune PhoBERT cho text correction
- Dùng `vinai/phobert-base`
- Fine-tune trên dataset Vietnamese text correction
- Tốt nhất nhưng cần thời gian và data

### Option 2: Dùng GPT-4o-mini (Recommended)
- Đã có sẵn, tốt nhất hiện tại
- Cần API key

### Option 3: Tìm model ready-to-use trên Hugging Face
- Search và test các model có sẵn
- Tích hợp vào system

### Option 4: Build custom dictionary + rules
- Tạo từ điển tiếng Việt lớn
- Rules cho dấu thanh điệu
- Nhanh nhưng ít chính xác

## Next Steps
1. Search Hugging Face cho Vietnamese text correction models
2. Test các models có sẵn
3. So sánh và chọn tốt nhất
4. Tích hợp vào system

