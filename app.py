"""
OCR Service Backend - Chuyên xử lý OCR tiếng Việt
Sử dụng PaddleOCR - thư viện OCR tốt nhất cho tiếng Việt
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import io
import base64
import time
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import cv2
import re  # Để check HTML tags
import requests  # Để gọi Text Correction API
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import OCR
from paddleocr import PaddleOCR

# Import Text/HTML utility functions
from text_html_utils import extract_text_from_html, text_to_html_paragraphs, text_to_html_paragraphs_with_alignment

# Text Correction API endpoint (load from .env, default to localhost:5001)
TEXT_CORRECTION_API_URL = os.getenv('TEXT_CORRECTION_API_URL', 'http://localhost:5001/correct')
TEXT_CORRECTION_AVAILABLE = True  # Luôn available vì dùng API

def correct_vietnamese_text(text, use_correction=True, use_gpu=False):
    """
    Gọi API Text Correction để chỉnh sửa chính tả tiếng Việt
    API endpoint: http://localhost:5001/correct
    GỌI MỘT LẦN cho toàn bộ text (không chia nhỏ) - NHANH và CHUẨN
    GPT-4o-mini sẽ tự động giữ nguyên format xuống dòng và spacing
    """
    if not use_correction or not text or not text.strip():
        return text
    
    try:
        # Gọi API một lần cho toàn bộ text - NHANH và CHUẨN
        response = requests.post(
            TEXT_CORRECTION_API_URL,
            json={'text': text},
            timeout=120  # Timeout 120 giây cho text dài
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                corrected_text = result.get('corrected_text', text)
                return corrected_text
            else:
                # Nếu API lỗi, giữ nguyên text gốc
                print(f"⚠️  API trả về lỗi: {result.get('error', 'Unknown error')}")
                return text
        else:
            # Nếu request failed, giữ nguyên text gốc
            print(f"⚠️  API request failed với status code: {response.status_code}")
            return text
            
    except requests.exceptions.ConnectionError:
        print(f"⚠️  Không thể kết nối đến Text Correction API ({TEXT_CORRECTION_API_URL})")
        print("💡 Đảm bảo API server đang chạy: cd ocr-protonx && python app.py")
        return text
    except requests.exceptions.Timeout:
        print("⚠️  API timeout (text quá dài hoặc server chậm), giữ nguyên text gốc")
        return text
    except Exception as e:
        print(f"⚠️  Lỗi khi gọi Text Correction API: {str(e)}")
        return text

print("\n" + "="*60)
print("📡 Text Correction: Sử dụng API")
print("="*60)
print(f"→ API endpoint: {TEXT_CORRECTION_API_URL}")
print("→ Sau khi PaddleOCR xong → Gọi API để sửa chính tả tiếng Việt")
print("="*60 + "\n")

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
# Hỗ trợ nhiều format PDF và image
ALLOWED_EXTENSIONS = {
    # PDF formats
    'pdf',
    # Image formats
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff', 'tif',
    'jfif', 'pjpeg', 'pjp', 'svg', 'ico', 'heic', 'heif'
}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize PaddleOCR với config tối ưu cho tiếng Việt - ĐẢM BẢO KHÔNG MẤT CHỮ
print("Đang khởi tạo PaddleOCR cho tiếng Việt...")
ocr_engine = PaddleOCR(
    use_angle_cls=True,  # Sử dụng góc độ classification
    lang='vi',  # Tiếng Việt
    use_gpu=False,  # Set True nếu có GPU
    show_log=False,
    # Config để đảm bảo không mất chữ
    det_db_thresh=0.3,  # Lower threshold để detect nhiều text hơn
    det_db_box_thresh=0.5,  # Lower để không bỏ sót
    rec_batch_num=6,  # Batch size để xử lý tốt hơn
    max_text_length=500  # Cho phép text dài hơn
)
print("✅ PaddleOCR đã sẵn sàng với config tối ưu!")

def allowed_file(filename):
    """Check if file extension is allowed"""
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def is_pdf_file(filename, file_buffer):
    """Check if file is PDF by content, not just extension"""
    try:
        # Check extension first (including cases where filename might be None or empty)
        if filename:
            filename_lower = filename.lower()
            if filename_lower.endswith('.pdf') or 'pdf' in filename_lower:
                # Verify by content too
                file_buffer.seek(0)
                header = file_buffer.read(4)
                file_buffer.seek(0)
                if header.startswith(b'%PDF'):
                    return True
        
        # Check magic bytes (PDF starts with %PDF) - primary check
        file_buffer.seek(0)
        # Read more bytes to be sure (PDF header can have whitespace)
        header = file_buffer.read(1024)
        file_buffer.seek(0)
        
        # Check for PDF magic bytes (can have whitespace before %PDF)
        if b'%PDF' in header[:1024]:
            return True
            
        # Also check for PDF in first bytes (sometimes Chrome adds data)
        if header.startswith(b'%PDF') or header.strip().startswith(b'%PDF'):
            return True
            
        return False
    except Exception as e:
        print(f"⚠️  Error checking PDF: {str(e)}")
        # Fallback: if filename suggests PDF, trust it
        if filename and filename.lower().endswith('.pdf'):
            return True
        return False

def is_image_file(filename, file_buffer):
    """Check if file is image by trying to open with PIL"""
    try:
        # First try to open with PIL (works for most formats)
        file_buffer.seek(0)
        buffer_copy = file_buffer.read()
        file_buffer.seek(0)
        
        # Try to open with PIL
        try:
            img = Image.open(io.BytesIO(buffer_copy))
            img.verify()  # Verify it's a valid image
            return True
        except:
            pass
        
        # Check extension as fallback
        if filename:
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            image_exts = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff', 'tif', 'jfif', 'pjpeg', 'pjp', 'ico', 'heic', 'heif'}
            if ext in image_exts:
                # Try again with format hint
                try:
                    file_buffer.seek(0)
                    img = Image.open(io.BytesIO(buffer_copy))
                    img.verify()
                    return True
                except:
                    pass
        return False
    except Exception as e:
        print(f"⚠️  Error checking image: {str(e)}")
        return False

def preprocess_image_for_ocr(image):
    """
    Preprocess image để tối ưu OCR cho tiếng Việt - KHÔNG LÀM MẤT CHỮ
    Preprocessing nhẹ để không làm mất thông tin text
    """
    try:
        # Đảm bảo image là RGB mode
        if image.mode != 'RGB':
            if image.mode == 'RGBA':
                # Tạo background trắng cho RGBA
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                image = rgb_image
            else:
                image = image.convert('RGB')
        
        # Convert PIL to OpenCV format
        img_array = np.array(image)
        
        # Đảm bảo là uint8
        if img_array.dtype != np.uint8:
            img_array = img_array.astype(np.uint8)
        
        # GIỮ NGUYÊN ảnh gốc nếu đã tốt - không preprocessing quá mạnh
        # Vì preprocessing có thể làm mất chữ hoặc làm sai text
        
        # Chỉ enhance contrast nhẹ nếu cần
        if len(img_array.shape) == 3:
            # Giữ color - không convert sang grayscale (có thể mất thông tin)
            img_processed = img_array.copy()
            # Enhance contrast nhẹ
            img_processed = cv2.convertScaleAbs(img_processed, alpha=1.2, beta=5)
        else:
            # Grayscale - enhance nhẹ
            img_processed = cv2.convertScaleAbs(img_array, alpha=1.3, beta=5)
        
        # Convert back to PIL
        if len(img_processed.shape) == 2:
            return Image.fromarray(img_processed, mode='L')
        elif len(img_processed.shape) == 3:
            return Image.fromarray(cv2.cvtColor(img_processed, cv2.COLOR_BGR2RGB))
        else:
            return image  # Return original nếu có vấn đề
    except Exception as e:
        print(f"⚠️  Lỗi khi preprocess image: {str(e)}, giữ nguyên image gốc")
        return image  # Return original nếu có lỗi

def extract_text_from_pdf(file_buffer):
    """
    Extract text từ PDF (nếu PDF có text layer)
    """
    doc = None
    try:
        # Đảm bảo file_buffer là bytes
        if isinstance(file_buffer, io.BytesIO):
            file_buffer.seek(0)
            file_buffer = file_buffer.read()
        elif not isinstance(file_buffer, bytes):
            file_buffer = bytes(file_buffer)
        
        doc = fitz.open(stream=file_buffer, filetype="pdf")
        total_pages = len(doc)
        text_parts = []
        
        for page_num in range(total_pages):
            try:
                page = doc[page_num]
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"--- Trang {page_num + 1} ---\n{text}")
            except Exception as page_err:
                print(f"  ⚠️  Lỗi khi đọc trang {page_num + 1}: {str(page_err)}")
                continue
        
        full_text = "\n\n".join(text_parts)
        
        # Phân tích chất lượng text
        text_length = len(full_text)
        word_count = len(full_text.split())
        has_vietnamese = any('\u0103' <= char <= '\u1ef9' or char in 'àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ' 
                           for char in full_text)
        
        is_real_text = text_length > 100 and word_count > 10 and has_vietnamese
        
        return {
            'text': full_text,
            'pages': total_pages,
            'text_length': text_length,
            'word_count': word_count,
            'is_real_text': is_real_text,
            'confidence': 100 if is_real_text else 30
        }
    except Exception as e:
        raise Exception(f"Lỗi khi đọc PDF: {str(e)}")
    finally:
        # Đảm bảo document được đóng
        if doc is not None:
            try:
                doc.close()
            except:
                pass

def pdf_to_images(file_buffer):
    """
    Convert PDF pages to images để OCR
    Xử lý từng trang với error handling - nếu một trang lỗi, skip và tiếp tục
    """
    try:
        # Đảm bảo file_buffer là bytes
        if isinstance(file_buffer, io.BytesIO):
            file_buffer.seek(0)
            file_buffer = file_buffer.read()
        elif not isinstance(file_buffer, bytes):
            file_buffer = bytes(file_buffer)
        
        doc = fitz.open(stream=file_buffer, filetype="pdf")
        total_pages = len(doc)
        images = []
        failed_pages = []
        
        print(f"📄 PDF có {total_pages} trang, đang chuyển sang ảnh...")
        
        try:
            for page_num in range(total_pages):
                pix = None
                try:
                    page = doc[page_num]
                    # Render với scale cao để OCR tốt hơn
                    mat = fitz.Matrix(2.5, 2.5)  # 2.5x scale
                    pix = page.get_pixmap(matrix=mat)
                    
                    # Convert to PIL Image
                    img_data = pix.tobytes("png")
                    # Copy image để tránh reference issues và đảm bảo độc lập
                    img = Image.open(io.BytesIO(img_data)).copy()
                    images.append(img)
                    print(f"  ✅ Trang {page_num + 1}/{total_pages} đã chuyển sang ảnh")
                except Exception as page_err:
                    print(f"  ⚠️  Lỗi khi chuyển trang {page_num + 1} sang ảnh: {str(page_err)}")
                    failed_pages.append(page_num + 1)
                    continue
                finally:
                    # Giải phóng pixmap để tránh memory leak
                    if pix is not None:
                        pix = None
        finally:
            # Đảm bảo document được đóng
            if doc is not None:
                try:
                    doc.close()
                except:
                    pass
        
        if failed_pages:
            print(f"⚠️  {len(failed_pages)} trang không thể chuyển sang ảnh: {failed_pages}")
        
        if not images:
            raise Exception("Không thể chuyển bất kỳ trang nào sang ảnh")
        
        print(f"✅ Đã chuyển {len(images)}/{total_pages} trang sang ảnh thành công")
        return images
    except Exception as e:
        raise Exception(f"Lỗi khi chuyển PDF sang ảnh: {str(e)}")

def detect_text_alignment(line_items, image_width):
    """
    Xác định alignment của text dựa trên vị trí bounding box
    Logic đơn giản và chính xác hơn:
    - So sánh margin trái và phải
    - Nếu margin trái << margin phải -> left
    - Nếu margin phải << margin trái -> right  
    - Nếu 2 margins tương đối bằng nhau -> center
    
    Returns: 'left', 'center', 'right'
    """
    if not line_items or not image_width or image_width <= 0:
        return 'left'
    
    # Tính vị trí của toàn bộ line (leftmost và rightmost)
    leftmost = min([item['x'] for item in line_items])
    rightmost = max([max([pt[0] for pt in item['box']]) for item in line_items])
    
    # Tính margins (khoảng cách từ edge) - tính bằng pixel
    left_margin_px = leftmost
    right_margin_px = image_width - rightmost
    
    # Tính độ rộng của line
    line_width = rightmost - leftmost
    
    # Tính tỷ lệ margins
    left_margin_ratio = left_margin_px / image_width
    right_margin_ratio = right_margin_px / image_width
    
    # Tính center của line
    line_center = (leftmost + rightmost) / 2
    center_ratio = line_center / image_width
    
    # Debug info - BẬT để test và debug alignment
    if len(line_items) > 0:
        first_text = line_items[0].get('text', '')[:20]
        print(f"  [Alignment] '{first_text}...' | L:{left_margin_px:.0f}px({left_margin_ratio:.1%}) R:{right_margin_px:.0f}px({right_margin_ratio:.1%}) C:{center_ratio:.1%} W:{line_width:.0f}px")
    
    # Tính chênh lệch margins
    margin_diff_px = abs(left_margin_px - right_margin_px)
    margin_diff_ratio = abs(left_margin_ratio - right_margin_ratio)
    
    # Rule 1: Nếu line chiếm > 90% width -> left (full width paragraph)
    if line_width / image_width > 0.90:
        result = 'left'
        print(f"    → Rule 1: Full width -> {result}")
        return result
    
    # Rule 2: So sánh margins trực tiếp - ĐƠN GIẢN NHẤT
    # Nếu chênh lệch margin < 3% image width HOẶC < 30px -> center
    threshold_px = max(30, image_width * 0.03)  # Ít nhất 30px hoặc 3% width
    if margin_diff_px < threshold_px:
        # Nhưng phải có margin ở cả 2 bên (không quá gần edge)
        if left_margin_ratio > 0.02 and right_margin_ratio > 0.02:
            result = 'center'
            print(f"    → Rule 2: Margins balanced -> {result}")
            return result
    
    # Rule 3: So sánh margins - left margin nhỏ hơn -> left
    if left_margin_px < right_margin_px:
        # Chênh lệch phải đáng kể (> 5% width hoặc > 50px)
        if (right_margin_px - left_margin_px) > max(50, image_width * 0.05):
            result = 'left'
            print(f"    → Rule 3: Left margin smaller -> {result}")
            return result
    
    # Rule 4: So sánh margins - right margin nhỏ hơn -> right
    if right_margin_px < left_margin_px:
        # Chênh lệch phải đáng kể (> 5% width hoặc > 50px)
        if (left_margin_px - right_margin_px) > max(50, image_width * 0.05):
            result = 'right'
            print(f"    → Rule 4: Right margin smaller -> {result}")
            return result
    
    # Rule 5: Dựa trên vị trí tuyệt đối (edge detection)
    if left_margin_ratio < 0.02:  # Rất gần edge trái
        result = 'left'
        print(f"    → Rule 5a: Near left edge -> {result}")
        return result
    
    if right_margin_ratio < 0.02:  # Rất gần edge phải
        result = 'right'
        print(f"    → Rule 5b: Near right edge -> {result}")
        return result
    
    # Rule 6: Fallback - dựa trên center position
    if center_ratio < 0.47:
        result = 'left'
    elif center_ratio > 0.53:
        result = 'right'
    else:
        result = 'center'
    
    print(f"    → Rule 6: Fallback (center={center_ratio:.1%}) -> {result}")
    return result

def format_line_with_spacing(line_items, image_width=None):
    """
    Format một dòng với spacing và xác định alignment
    Sử dụng bounding boxes để tính toán chính xác vị trí và spacing
    """
    if not line_items:
        return {"text": "", "alignment": "left"}
    
    # Sort by X position (left to right)
    line_items.sort(key=lambda x: x['x'])
    
    # Xác định alignment
    alignment = 'left'
    if image_width and image_width > 0:
        alignment = detect_text_alignment(line_items, image_width)
    
    # Format text với spacing
    if len(line_items) > 1:
        # Calculate spacing between items dựa trên bounding boxes
        spacings = []
        for i in range(len(line_items) - 1):
            # Calculate end of current item (rightmost x)
            current_end = max([pt[0] for pt in line_items[i]['box']])
            # Calculate start of next item (leftmost x)
            next_start = line_items[i + 1]['x']
            spacing = next_start - current_end
            spacings.append(spacing)
        
        # Format with multiple spaces để preserve alignment - GIỮ FORMAT PDF
        result_parts = []
        for i, item in enumerate(line_items):
            text = item.get('text', '')
            if not text:  # Skip nếu không có text
                continue
                
            if i > 0:
                # Add spaces based on spacing - chính xác hơn
                # ~6-8px per space character (tùy font)
                pixel_spacing = spacings[i-1]
                spaces_needed = max(1, int(pixel_spacing / 7))  # 7px per space
                # Giới hạn tối đa 20 spaces để tránh quá dài
                result_parts.append(' ' * min(spaces_needed, 20))
            # Strip chỉ ở đầu/cuối, giữ nguyên spaces trong text
            result_parts.append(text.strip() if text.strip() else text)
        
        text_result = ''.join(result_parts) if result_parts else ''
    else:
        # Single item - join với space, GIỮ NGUYÊN tất cả text
        texts = []
        for item in line_items:
            text = item.get('text', '')
            if text:  # Chỉ thêm nếu có text
                # Strip chỉ ở đầu/cuối, giữ nguyên spaces trong text
                texts.append(text.strip() if text.strip() else text)
        
        text_result = ' '.join(texts) if texts else ''
    
    return {"text": text_result, "alignment": alignment}

def ocr_image(image, use_preprocessing=False):
    """
    OCR một ảnh với PaddleOCR - Giữ layout (tables, columns, spacing)
    ĐẢM BẢO KHÔNG MẤT CHỮ - Default: TẮT preprocessing để không làm mất text
    """
    try:
        # Preprocess NHẸ nếu cần - Default TẮT để không làm mất chữ
        if use_preprocessing:
            print("⚠️  Preprocessing enabled - có thể ảnh hưởng đến chất lượng text")
            image = preprocess_image_for_ocr(image)
        
        # Convert PIL to numpy array for PaddleOCR
        # Đảm bảo image là RGB mode trước
        if image.mode != 'RGB':
            if image.mode == 'RGBA':
                # Tạo background trắng cho RGBA
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[3] if image.mode == 'RGBA' else None)
                image = rgb_image
            else:
                image = image.convert('RGB')
        
        img_array = np.array(image)
        
        # Đảm bảo img_array có format đúng
        if len(img_array.shape) == 2:
            # Grayscale -> convert to BGR
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif len(img_array.shape) == 3:
            # Color image - PIL là RGB, PaddleOCR cần BGR
            if img_array.shape[2] == 4:  # RGBA (should not happen after conversion above)
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            elif img_array.shape[2] == 3:  # RGB
                img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                raise Exception(f"Unsupported image format: {img_array.shape}")
        else:
            raise Exception(f"Invalid image array shape: {img_array.shape}")
        
        # Đảm bảo img_array là uint8
        if img_array.dtype != np.uint8:
            img_array = img_array.astype(np.uint8)
        
        # Perform OCR - ĐẢM BẢO KHÔNG MẤT CHỮ
        result = ocr_engine.ocr(img_array, cls=True)
        
        # Debug: Log kết quả OCR
        if result:
            total_detected = len(result[0]) if result[0] else 0
            print(f"📊 PaddleOCR detected {total_detected} text items")
        
        # Extract text với layout preservation - ĐẢM BẢO KHÔNG MẤT CHỮ
        texts = []
        confidences = []
        lines_with_alignment = []  # Store alignment info
        
        if result and result[0]:
            # Extract TẤT CẢ text từ PaddleOCR - KHÔNG BỎ SÓT
            lines_sorted = []
            total_items = 0
            skipped_items = 0
            
            for line in result[0]:
                if line and len(line) >= 2:
                    try:
                        box = line[0]  # Bounding box
                        text_info = line[1]  # [text, confidence]
                        
                        # Đảm bảo text_info là list/tuple và có ít nhất text
                        if isinstance(text_info, (list, tuple)) and len(text_info) > 0:
                            text = str(text_info[0]) if text_info[0] else ""
                            confidence = float(text_info[1]) if len(text_info) > 1 else 0.0
                        else:
                            # Fallback: text_info có thể là string
                            text = str(text_info) if text_info else ""
                            confidence = 0.0
                        
                        # KHÔNG FILTER - Lấy TẤT CẢ text, kể cả confidence thấp hoặc text có vấn đề
                        # Chỉ skip nếu text là None hoặc hoàn toàn rỗng (không có ký tự nào)
                        if text is None:
                            skipped_items += 1
                            continue
                        
                        # Giữ cả text chỉ có spaces (có thể là dòng trống hoặc spacing)
                        # Chỉ skip nếu thực sự không có ký tự nào
                        text_str = str(text).strip()
                        if not text_str:
                            skipped_items += 1
                            continue
                        
                        y_pos = min([pt[1] for pt in box])
                        x_pos = min([pt[0] for pt in box])
                        lines_sorted.append({
                            'y': y_pos,
                            'x': x_pos,
                            'text': text,  # Giữ nguyên text, không strip ở đây
                            'confidence': confidence,
                            'box': box
                        })
                        total_items += 1
                    except Exception as e:
                        print(f"⚠️  Lỗi khi extract text từ line: {str(e)}, line: {line}")
                        skipped_items += 1
                        continue
            
            print(f"📊 OCR Extraction Stats:")
            print(f"   ✅ Extracted: {total_items} items")
            print(f"   ⚠️  Skipped: {skipped_items} items (empty text)")
            print(f"   📈 Success rate: {(total_items / len(result[0]) * 100) if result[0] else 0:.1f}%")
            
            # Sort by Y position (top to bottom), then X (left to right)
            lines_sorted.sort(key=lambda x: (round(x['y'] / 10) * 10, x['x']))
            
            # Get image width từ image size - QUAN TRỌNG cho alignment detection
            img_width = img_array.shape[1] if len(img_array.shape) > 1 else None
            if img_width is None or img_width <= 0:
                # Fallback: tính từ bounding boxes nếu có
                if result and result[0] and len(result[0]) > 0:
                    all_x_coords = []
                    for line in result[0]:
                        if line and len(line) >= 2:
                            box = line[0]
                            all_x_coords.extend([pt[0] for pt in box])
                    if all_x_coords:
                        img_width = max(all_x_coords) + 50  # Thêm margin
                else:
                    img_width = 1000  # Default fallback
            
            # Group into lines and preserve layout với alignment
            current_line_items = []
            current_line_y = None
            lines_with_alignment = []  # Store lines with alignment info
            
            for item in lines_sorted:
                # Group items on same line (Y position similar)
                # Tăng threshold để group tốt hơn và không mất text
                if current_line_y is None or abs(item['y'] - current_line_y) < 20:
                    current_line_items.append(item)
                    if current_line_y is None:
                        current_line_y = item['y']
                else:
                    # New line - format previous line với layout và alignment
                    if current_line_items:
                        formatted_result = format_line_with_spacing(current_line_items, img_width)
                        formatted_line = formatted_result.get('text', '')
                        alignment = formatted_result.get('alignment', 'left')
                        
                        # Đảm bảo không mất text - nếu formatted_line rỗng nhưng có text, dùng text gốc
                        if not formatted_line or not formatted_line.strip():
                            # Fallback: join tất cả text từ items
                            fallback_text = ' '.join([item['text'] for item in current_line_items if item.get('text')])
                            if fallback_text:
                                formatted_line = fallback_text
                        
                        if formatted_line:  # Chỉ append nếu có text
                            texts.append(formatted_line)
                            confidences.append(sum([i['confidence'] for i in current_line_items]) / len(current_line_items))
                            lines_with_alignment.append({
                                'text': formatted_line,
                                'alignment': alignment
                            })
                    
                    current_line_items = [item]
                    current_line_y = item['y']
            
            # Process last line
            if current_line_items:
                formatted_result = format_line_with_spacing(current_line_items, img_width)
                formatted_line = formatted_result.get('text', '')
                alignment = formatted_result.get('alignment', 'left')
                
                # Đảm bảo không mất text
                if not formatted_line or not formatted_line.strip():
                    fallback_text = ' '.join([item['text'] for item in current_line_items if item.get('text')])
                    if fallback_text:
                        formatted_line = fallback_text
                
                if formatted_line:  # Chỉ append nếu có text
                    texts.append(formatted_line)
                    confidences.append(sum([i['confidence'] for i in current_line_items]) / len(current_line_items))
                    lines_with_alignment.append({
                        'text': formatted_line,
                        'alignment': alignment
                    })
        
        full_text = "\n".join(texts)
        avg_confidence = sum(confidences) / len(confidences) * 100 if confidences else 0
        
        return {
            'text': full_text,
            'confidence': avg_confidence,
            'words': len(texts),
            'lines_with_alignment': lines_with_alignment  # Thêm alignment info
        }
    except Exception as e:
        raise Exception(f"Lỗi khi OCR ảnh: {str(e)}")

def process_pdf(file_buffer, force_ocr=False, use_text_correction=True):
    """
    Xử lý PDF file - thử extract text trước, nếu không được thì OCR
    """
    start_time = time.time()
    
    # Đảm bảo file_buffer là bytes (handle trường hợp Chrome PDF viewer)
    if isinstance(file_buffer, io.BytesIO):
        file_buffer.seek(0)
        file_buffer = file_buffer.read()
    elif not isinstance(file_buffer, bytes):
        file_buffer = bytes(file_buffer)
    
    # Thử extract text trước
    if not force_ocr:
        try:
            extracted = extract_text_from_pdf(file_buffer)
            if extracted['is_real_text'] and extracted['confidence'] >= 80:
                text = extracted['text']
                
                # Apply text correction qua API - sửa chính tả tiếng Việt
                corrected_text = text
                if use_text_correction and TEXT_CORRECTION_AVAILABLE:
                    print("Đang gọi Text Correction API để sửa chính tả tiếng Việt...")
                    corrected_text = correct_vietnamese_text(text, use_correction=True)
                
                processing_time = time.time() - start_time
                
                # PHÂN TÁCH: text (text thuần) và html (HTML)
                # Nếu corrected_text có HTML tags -> extract text thuần và giữ HTML
                # Nếu corrected_text là text thuần -> giữ text và convert sang HTML
                has_html_tags = '<' in corrected_text and '>' in corrected_text and re.search(r'<[^>]+>', corrected_text)
                
                if has_html_tags:
                    # Text đang chứa HTML -> extract text thuần
                    plain_text = extract_text_from_html(corrected_text)
                    html_content = corrected_text
                else:
                    # Text thuần -> convert sang HTML
                    plain_text = corrected_text
                    html_content = text_to_html_paragraphs(corrected_text)
                
                result_data = {
                    'success': True,
                    'text': plain_text,  # Text thuần (không có HTML tags)
                    'html': html_content,  # HTML (có HTML tags)
                    'pages': extracted['pages'],
                    'confidence': extracted['confidence'],
                    'method': 'direct_extraction',
                    'text_correction': use_text_correction and TEXT_CORRECTION_AVAILABLE,
                    'processing_time': f"{processing_time:.2f}s",
                    'text_length': len(plain_text),
                    'word_count': len(plain_text.split())
                }
                
                return result_data
        except Exception as e:
            print(f"Text extraction failed: {e}")
    
    # Nếu không được, OCR
    print("PDF không có text layer tốt, đang OCR...")
    
    try:
        # Convert PDF to images
        images = pdf_to_images(file_buffer)
        print(f"Đã chuyển đổi {len(images)} trang sang ảnh")
        
        # OCR từng trang và gọi ProtonX sửa chính tả ngay sau mỗi trang
        # Xử lý từng trang với error handling riêng - nếu một trang lỗi, skip và tiếp tục
        all_texts = []
        all_confidences = []
        failed_pages = []
        
        for idx, img in enumerate(images):
            try:
                print(f"\n[{idx + 1}/{len(images)}] Đang OCR trang {idx + 1}...")
                
                # OCR trang này - đảm bảo image được copy để tránh reference issues
                try:
                    # Copy image để đảm bảo độc lập
                    img_copy = img.copy() if hasattr(img, 'copy') else img
                    result = ocr_image(img_copy, use_preprocessing=False)  # TẮT preprocessing để không mất chữ
                except Exception as ocr_err:
                    print(f"  ⚠️  Lỗi khi OCR trang {idx + 1}: {str(ocr_err)}")
                    failed_pages.append(idx + 1)
                    all_texts.append(f"--- Trang {idx + 1} ---\n[Lỗi khi OCR trang này: {str(ocr_err)}]")
                    all_confidences.append(0.0)
                    continue
                
                if result and result.get('text'):
                    page_text = result['text']
                    
                    # Gọi API ngay sau khi OCR xong từng trang để sửa chính tả
                    if use_text_correction and TEXT_CORRECTION_AVAILABLE:
                        try:
                            print(f"  → Gọi Text Correction API để sửa chính tả tiếng Việt trang {idx + 1}...")
                            corrected_page_text = correct_vietnamese_text(page_text, use_correction=True)
                            print(f"  ✅ Đã sửa chính tả trang {idx + 1} xong")
                            all_texts.append(f"--- Trang {idx + 1} ---\n{corrected_page_text}")
                        except Exception as correction_err:
                            print(f"  ⚠️  Lỗi khi sửa chính tả trang {idx + 1}: {str(correction_err)}, giữ nguyên text gốc")
                            all_texts.append(f"--- Trang {idx + 1} ---\n{page_text}")
                    else:
                        all_texts.append(f"--- Trang {idx + 1} ---\n{page_text}")
                    
                    all_confidences.append(result.get('confidence', 0.0))
                else:
                    print(f"  ⚠️  Trang {idx + 1} không có text được detect")
                    all_texts.append(f"--- Trang {idx + 1} ---\n[Không có text được phát hiện]")
                    all_confidences.append(0.0)
                    
            except Exception as page_err:
                print(f"  ❌ Lỗi khi xử lý trang {idx + 1}: {str(page_err)}")
                failed_pages.append(idx + 1)
                all_texts.append(f"--- Trang {idx + 1} ---\n[Lỗi: {str(page_err)}]")
                all_confidences.append(0.0)
                continue
        
        # Log kết quả
        success_pages = len(images) - len(failed_pages)
        print(f"\n📊 Kết quả xử lý PDF:")
        print(f"   ✅ Thành công: {success_pages}/{len(images)} trang")
        if failed_pages:
            print(f"   ⚠️  Lỗi: {len(failed_pages)} trang ({', '.join(map(str, failed_pages))})")
        
        # Kết hợp tất cả các trang đã được sửa chính tả
        combined_text = "\n\n".join(all_texts)
        
        # PHÂN TÁCH: text (text thuần) và html (HTML)
        # Nếu combined_text có HTML tags -> extract text thuần và giữ HTML
        # Nếu combined_text là text thuần -> giữ text và convert sang HTML
        has_html_tags = '<' in combined_text and '>' in combined_text and re.search(r'<[^>]+>', combined_text)
        
        if has_html_tags:
            # Text đang chứa HTML -> extract text thuần
            plain_text = extract_text_from_html(combined_text)
            html_content = combined_text
        else:
            # Text thuần -> convert sang HTML (không có alignment info từ PDF extraction)
            plain_text = combined_text
            html_content = text_to_html_paragraphs(combined_text)
        
        avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0
        processing_time = time.time() - start_time
        
        # Tính số trang thành công
        success_pages = len(images) - len(failed_pages) if failed_pages else len(images)
        
        result = {
            'success': True,
            'text': plain_text,  # Text thuần (không có HTML tags)
            'html': html_content,  # HTML (có HTML tags)
            'pages': len(images),
            'success_pages': success_pages,
            'failed_pages': failed_pages if failed_pages else [],
            'confidence': avg_confidence,
            'method': 'ocr',
            'text_correction': use_text_correction and TEXT_CORRECTION_AVAILABLE,
            'processing_time': f"{processing_time:.2f}s",
            'text_length': len(plain_text),
            'word_count': len(plain_text.split())
        }
        
        # Nếu có trang lỗi, vẫn trả về success nhưng có warning
        if failed_pages:
            result['warning'] = f"Một số trang ({len(failed_pages)} trang) không thể xử lý được"
        
        return result
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            'success': False,
            'text': '',
            'error': f"Lỗi khi OCR PDF: {str(e)}",
            'processing_time': f"{processing_time:.2f}s",
            'method': 'ocr_failed'
        }

def process_image(file_buffer, use_text_correction=True):
    """
    Xử lý image file
    """
    start_time = time.time()
    
    try:
        # Open image - PIL sẽ tự động handle nhiều format (PNG, JPG, GIF, BMP, WEBP, TIFF, etc.)
        try:
            image = Image.open(io.BytesIO(file_buffer))
            # Verify image is valid
            image.verify()
            # Reopen because verify() closes the image
            image = Image.open(io.BytesIO(file_buffer))
        except Exception as img_error:
            raise Exception(f"Không thể mở file ảnh: {str(img_error)}. Vui lòng đảm bảo file là ảnh hợp lệ (PNG, JPG, JPEG, GIF, BMP, WEBP, TIFF, etc.)")
        
        # OCR
        result = ocr_image(image, use_preprocessing=False)  # TẮT preprocessing để không mất chữ
        
        # Apply text correction qua API - sửa chính tả tiếng Việt
        text = result['text']
        lines_with_alignment = result.get('lines_with_alignment', [])
        
        if use_text_correction and TEXT_CORRECTION_AVAILABLE:
            print("Đang gọi Text Correction API để sửa chính tả tiếng Việt...")
            text = correct_vietnamese_text(text, use_correction=True)
            # Cập nhật text trong lines_with_alignment sau khi correction
            # (giữ nguyên alignment, chỉ update text)
            corrected_lines = text.split('\n')
            for i, line_info in enumerate(lines_with_alignment):
                if i < len(corrected_lines):
                    line_info['text'] = corrected_lines[i]
        
        processing_time = time.time() - start_time
        
        # PHÂN TÁCH: text (text thuần) và html (HTML)
        # Nếu text có HTML tags -> extract text thuần và giữ HTML
        # Nếu text là text thuần -> giữ text và convert sang HTML với alignment
        has_html_tags = '<' in text and '>' in text and re.search(r'<[^>]+>', text)
        
        if has_html_tags:
            # Text đang chứa HTML -> extract text thuần
            plain_text = extract_text_from_html(text)
            html_content = text
        else:
            # Text thuần -> convert sang HTML với alignment
            plain_text = text
            html_content = text_to_html_paragraphs_with_alignment(text, lines_with_alignment)
        
        result_data = {
            'success': True,
            'text': plain_text,  # Text thuần (không có HTML tags)
            'html': html_content,  # HTML (có HTML tags)
            'confidence': result['confidence'],
            'method': 'ocr',
            'text_correction': use_text_correction and TEXT_CORRECTION_AVAILABLE,
            'processing_time': f"{processing_time:.2f}s",
            'text_length': len(plain_text),
            'word_count': len(plain_text.split())
        }
        
        return result_data
    except Exception as e:
        processing_time = time.time() - start_time
        return {
            'success': False,
            'text': '',
            'error': f"Lỗi khi OCR ảnh: {str(e)}",
            'processing_time': f"{processing_time:.2f}s",
            'method': 'ocr_failed'
        }

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'message': 'OCR service đang hoạt động bình thường',
        'engine': 'PaddleOCR',
        'language': 'Vietnamese (vi)',
        'text_correction': {
            'available': TEXT_CORRECTION_AVAILABLE,
            'method': 'api',
            'api_url': TEXT_CORRECTION_API_URL if TEXT_CORRECTION_AVAILABLE else None,
            'description': 'Sau khi PaddleOCR lấy text → Gọi API để sửa chính tả tiếng Việt chuẩn' if TEXT_CORRECTION_AVAILABLE else None
        },
        'supported_formats': list(ALLOWED_EXTENSIONS)
    })

@app.route('/extract-text', methods=['POST'])
def extract_text():
    """
    Extract text from PDF or Image
    POST /extract-text
    FormData: file (PDF or Image), forceOCR (optional), language (optional)
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'Không có file được upload'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'Không có file được chọn'
            }), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'message': f'File quá lớn. Kích thước tối đa: {MAX_FILE_SIZE / 1024 / 1024}MB'
            }), 400
        
        # Read file to buffer first (need to check content type)
        # Reset file pointer trước khi đọc
        file.seek(0)
        file_buffer = file.read()
        # Tạo BytesIO mới để đảm bảo clean state
        file_buffer_io = io.BytesIO(file_buffer)
        file_buffer_io.seek(0)
        
        # Check file type by content, not just extension (more flexible)
        # Also check content-type header (Chrome PDF viewer might send application/pdf)
        content_type = request.content_type or request.headers.get('Content-Type', '') or ''
        filename_lower = (file.filename or '').lower()
        
        # Check if it's PDF first (by content-type, filename, or content)
        is_pdf = False
        # Check content-type header (Chrome PDF viewer sends application/pdf)
        if 'application/pdf' in content_type:
            is_pdf = True
            print(f"✅ Detected PDF by Content-Type: {content_type}")
        elif filename_lower.endswith('.pdf'):
            # Check by content to verify
            is_pdf = is_pdf_file(file.filename, file_buffer_io)
            if is_pdf:
                print(f"✅ Detected PDF by filename and content: {file.filename}")
        else:
            # Check by content only
            is_pdf = is_pdf_file(file.filename, file_buffer_io)
            if is_pdf:
                print(f"✅ Detected PDF by content (no extension): {file.filename}")
        
        # If not PDF, check if it's image
        is_image = False
        if not is_pdf:
            # Check content-type for images
            if any(ct in content_type for ct in ['image/', 'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp', 'image/tiff']):
                is_image = is_image_file(file.filename, file_buffer_io)
            else:
                is_image = is_image_file(file.filename, file_buffer_io)
        
        if not is_pdf and not is_image:
            # Try extension check as fallback
            if not allowed_file(file.filename):
                return jsonify({
                    'success': False,
                    'message': f'File type không được hỗ trợ. Hỗ trợ: PDF và các định dạng ảnh (PNG, JPG, JPEG, GIF, BMP, WEBP, TIFF, etc.)'
                }), 400
        
        # Get options
        force_ocr = request.form.get('forceOCR', 'false').lower() == 'true'
        use_text_correction = request.form.get('useTextCorrection', 'true').lower() == 'true'  # Default: enabled
        
        # Process based on detected file type (use content detection)
        if is_pdf:
            result = process_pdf(file_buffer, force_ocr=force_ocr, use_text_correction=use_text_correction)
        elif is_image:
            result = process_image(file_buffer, use_text_correction=use_text_correction)
        else:
            return jsonify({
                'success': False,
                'message': 'Không thể xác định loại file. Vui lòng upload file PDF hoặc ảnh hợp lệ.'
            }), 400
        
        # Return result
        if result.get('success'):
            # Debug: Check if HTML is in result
            if 'html' in result:
                print(f"✅ Returning result with HTML (length: {len(result['html'])})")
            else:
                print("⚠️  Returning result WITHOUT HTML")
            return jsonify(result)
        else:
            return jsonify(result), 200  # Return 200 but with error in body
        
    except Exception as e:
        print(f"Error in extract_text: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Đã xảy ra lỗi: {str(e)}',
            'error': str(e)
        }), 500
    finally:
        # Cleanup - đảm bảo không có resource leak sau mỗi request
        import gc
        gc.collect()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 4000))  # Port 4000 cho OCR service, 5001 cho Text Correction API
    print(f"🚀 OCR Service đang chạy trên port {port}")
    print(f"📝 Chuyên xử lý OCR tiếng Việt với PaddleOCR")
    print(f"💡 Text Correction API: {TEXT_CORRECTION_API_URL}")
    app.run(host='0.0.0.0', port=port, debug=False)

