# Fix Torch DLL Error trên Windows - HƯỚNG DẪN CHI TIẾT

## Lỗi bạn đang gặp
```
[WinError 127] The specified procedure could not be found. 
Error loading "...\torch\lib\shm.dll" or one of its dependencies.
```

## 🔧 Giải pháp (Thử theo thứ tự)

### Solution 1: Cài Visual C++ Redistributable (NHANH NHẤT)

1. **Download Visual C++ Redistributable**:
   - Link: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Hoặc tìm "Visual C++ Redistributable 2015-2022 x64"

2. **Cài đặt**:
   - Chạy file .exe vừa download
   - Chọn "Install"
   - Chờ cài đặt xong

3. **Restart**:
   - Đóng tất cả terminal/IDE
   - Mở lại terminal
   - Chạy lại app

### Solution 2: Cài lại torch (Nếu Solution 1 không được)

```bash
# Uninstall torch cũ
pip uninstall torch torchvision torchaudio -y

# Cài lại torch CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Hoặc cài version cụ thể
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu
```

### Solution 3: Dùng GPT-4o-mini thay thế (Tạm thời)

Nếu torch vẫn không hoạt động, có thể dùng GPT-4o-mini:

1. Set OPENAI_API_KEY:
   ```bash
   set OPENAI_API_KEY=sk-your-key-here
   ```

2. Hệ thống sẽ tự động dùng GPT làm fallback

## ⚠️ Lưu ý

- Solution 1 (Visual C++) thường fix được 90% trường hợp
- Solution 2 cần thời gian để cài lại torch
- Solution 3 là giải pháp tạm thời, vẫn tốt nhưng có chi phí

## Test sau khi fix

Chạy test script:
```bash
python test_protonx_simple.py
```

Nếu thấy "✅ Model đã sửa chính tả!" → OK!
