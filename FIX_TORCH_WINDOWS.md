# Fix Torch DLL Error trên Windows

## Lỗi
```
[WinError 127] The specified procedure could not be found. 
Error loading "...\torch\lib\shm.dll" or one of its dependencies.
```

## Giải pháp

### Solution 1: Cài Visual C++ Redistributable (Recommended)
1. Download: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Cài đặt
3. Restart terminal/IDE
4. Chạy lại app

### Solution 2: Cài lại torch
```bash
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

### Solution 3: Dùng GPT-4o-mini thay thế
Nếu torch không thể fix, có thể dùng GPT-4o-mini API thay thế

## Tạm thời: Dùng GPT làm fallback

Nếu torch không hoạt động, hệ thống sẽ tự động dùng GPT-4o-mini (nếu có API key)

