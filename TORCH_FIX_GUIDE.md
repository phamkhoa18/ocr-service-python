# 🔧 Hướng Dẫn Fix Lỗi Torch DLL trên Windows

## Lỗi bạn đang gặp
```
[WinError 127] The specified procedure could not be found.
Error loading "...\torch\lib\shm.dll" or one of its dependencies.
```

## ✅ Giải Pháp (Thử theo thứ tự)

### Giải Pháp 1: Cài Visual C++ Redistributable (90% fix được)

1. **Download Visual C++ Redistributable**:
   - Link: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Hoặc tìm "Visual C++ Redistributable 2015-2022 x64"

2. **Cài đặt**:
   - Chạy file .exe vừa download
   - Chọn "Install"
   - Đợi cài xong

3. **Restart**:
   - Đóng tất cả terminal/PowerShell/CMD
   - Đóng IDE (VS Code, PyCharm, ...)
   - Mở lại terminal
   - Chạy lại app: `python app.py`

### Giải Pháp 2: Cài lại torch (Nếu Giải Pháp 1 không được)

**Cách 1: Dùng script tự động**
```bash
# Chạy script
QUICK_FIX_TORCH.bat
```

**Cách 2: Làm thủ công**
```bash
# Uninstall torch cũ
pip uninstall torch torchvision torchaudio -y

# Cài lại torch CPU version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Test
python -c "import torch; print('✅ Torch OK:', torch.__version__)"
```

### Giải Pháp 3: Cài torch version cũ hơn

```bash
pip uninstall torch torchvision torchaudio -y
pip install torch==2.0.0 torchvision==0.15.0 torchaudio==2.0.0 --index-url https://download.pytorch.org/whl/cpu
```

### Giải Pháp 4: Dùng GPT-4o-mini thay thế (Tạm thời)

Nếu torch vẫn không fix được, dùng GPT:

```bash
# Set API key
set OPENAI_API_KEY=sk-your-key-here

# Hệ thống sẽ tự động dùng GPT làm fallback
```

## ⚠️ Lưu ý

- **Giải Pháp 1** thường fix được 90% trường hợp → Thử đầu tiên!
- **Giải Pháp 2** cần thời gian cài lại torch
- **Giải Pháp 4** là tạm thời, vẫn tốt nhưng có chi phí

## Test sau khi fix

```bash
# Test torch
python -c "import torch; print('✅ Torch:', torch.__version__)"

# Test ProtonX model
python test_protonx_simple.py

# Chạy app
python app.py
```

## Nếu vẫn lỗi

1. Check Python version: `python --version` (nên dùng 3.8-3.11)
2. Check pip version: `pip --version`
3. Thử cài torch trong virtual environment mới:
   ```bash
   python -m venv venv_new
   venv_new\Scripts\activate
   pip install torch --index-url https://download.pytorch.org/whl/cpu
   ```

