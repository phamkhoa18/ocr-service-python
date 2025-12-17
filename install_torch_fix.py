"""
Script tự động fix lỗi torch DLL trên Windows
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("="*60)
    print("🔧 TỰ ĐỘNG FIX LỖI TORCH DLL TRÊN WINDOWS")
    print("="*60)
    
    # Step 1: Uninstall torch cũ
    print("\n1️⃣  Đang gỡ cài đặt torch cũ...")
    success, stdout, stderr = run_command("pip uninstall torch torchvision torchaudio -y")
    if success:
        print("   ✅ Đã gỡ cài đặt torch cũ")
    else:
        print(f"   ⚠️  {stderr}")
    
    # Step 2: Cài lại torch CPU
    print("\n2️⃣  Đang cài lại torch CPU version...")
    print("   ⚠️  Có thể mất vài phút...")
    
    cmd = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu"
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("   ✅ Đã cài đặt torch thành công")
    else:
        print(f"   ❌ Lỗi khi cài đặt: {stderr}")
        print("\n💡 Thử cách khác:")
        print("   1. Cài Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("   2. Restart terminal và chạy lại script")
        return False
    
    # Step 3: Test torch
    print("\n3️⃣  Đang test torch...")
    test_code = "import torch; print(torch.__version__)"
    success, stdout, stderr = run_command(f'python -c "{test_code}"')
    
    if success and "torch" in stdout.lower() or stdout.strip():
        print(f"   ✅ Torch đã hoạt động! Version: {stdout.strip()}")
        return True
    else:
        print(f"   ❌ Torch vẫn chưa hoạt động: {stderr}")
        print("\n💡 Cần cài Visual C++ Redistributable:")
        print("   https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "="*60)
        print("✅ HOÀN THÀNH! Torch đã được fix")
        print("="*60)
        print("\nBây giờ có thể chạy app.py và ProtonX sẽ hoạt động!")
    else:
        print("\n" + "="*60)
        print("❌ CHƯA FIX ĐƯỢC")
        print("="*60)
        print("\nVui lòng:")
        print("1. Cài Visual C++ Redistributable: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("2. Restart terminal")
        print("3. Chạy lại script này")

