@echo off
echo ============================================================
echo FIX TORCH DLL ERROR - QUICK FIX SCRIPT
echo ============================================================
echo.

echo Step 1: Uninstall torch cũ...
pip uninstall torch torchvision torchaudio -y

echo.
echo Step 2: Cài lại torch CPU version...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

echo.
echo Step 3: Test torch...
python -c "import torch; print('✅ Torch version:', torch.__version__)"

echo.
echo ============================================================
echo NẾU VẪN LỖI:
echo 1. Download và cài Visual C++ Redistributable:
echo    https://aka.ms/vs/17/release/vc_redist.x64.exe
echo 2. Restart terminal và chạy lại script này
echo ============================================================
pause

