# ⚠️ LỖI TORCH DLL - HƯỚNG DẪN FIX NHANH

## Bạn đang gặp lỗi này?

```
[WinError 127] The specified procedure could not be found.
Error loading "...\torch\lib\shm.dll"
```

## 🚀 FIX NHANH (90% trường hợp)

### Cách 1: Cài Visual C++ Redistributable (NHANH NHẤT - 2 phút)

1. **Download**: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. **Cài đặt**: Chạy file .exe → Install
3. **Restart**: Đóng và mở lại terminal
4. **Test**: `python -c "import torch; print('OK')"`

### Cách 2: Chạy script tự động

```bash
python install_torch_fix.py
```

Hoặc:

```bash
QUICK_FIX_TORCH.bat
```

### Cách 3: Fix thủ công

```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

## ✅ Sau khi fix

Chạy lại app.py và bạn sẽ thấy:
```
✅ ProtonX Text Correction Model đã sẵn sàng!
```

## ⚠️ Nếu vẫn không được

1. Check Python version: `python --version` (nên 3.8-3.11)
2. Thử cài Visual C++ Redistributable (Cách 1)
3. Hoặc dùng GPT-4o-mini làm fallback (Set OPENAI_API_KEY)

