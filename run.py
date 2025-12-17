#!/usr/bin/env python3
"""
Script để chạy OCR Service
"""
import os
from dotenv import load_dotenv
from app import app

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    
    print("=" * 60)
    print("🚀 OCR Service - Chuyên xử lý OCR tiếng Việt")
    print("=" * 60)
    print(f"📝 Engine: PaddleOCR")
    print(f"🌐 Port: {port}")
    print(f"🔗 URL: http://localhost:{port}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=debug)

