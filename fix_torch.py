"""
Script để fix torch DLL error trên Windows
"""

print("🔧 Fixing torch DLL error...")

# Option 1: Uninstall và reinstall torch
print("\nOption 1: Reinstall torch (CPU version - ít lỗi hơn)")
print("Chạy các lệnh sau:")
print("  pip uninstall torch torchvision torchaudio -y")
print("  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu")

# Option 2: Check if Visual C++ Redistributable is needed
print("\nOption 2: Cài Visual C++ Redistributable")
print("Download từ: https://aka.ms/vs/17/release/vc_redist.x64.exe")

# Option 3: Disable text correction
print("\nOption 3: Tạm thời disable text correction")
print("Service vẫn chạy bình thường, chỉ không có text correction")
print("Sửa trong app.py: TEXT_CORRECTION_AVAILABLE = False")

print("\n✅ Service sẽ chạy được ngay cả khi torch fail!")
print("   OCR vẫn hoạt động bình thường, chỉ không có text correction.")

