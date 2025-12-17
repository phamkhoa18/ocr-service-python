"""
Improved OCR với Layout Preservation
Sử dụng PaddleOCR với layout detection để giữ cấu trúc văn bản
"""

import re
from typing import List, Dict, Tuple

def ocr_with_layout_preservation(ocr_result, image_width):
    """
    OCR với layout preservation
    PaddleOCR trả về bounding boxes, sử dụng để giữ layout
    """
    if not ocr_result or not ocr_result[0]:
        return ""
    
    # Sort lines by Y position (top to bottom)
    lines_with_pos = []
    for line in ocr_result[0]:
        if line:
            box = line[0]  # Bounding box coordinates
            text_info = line[1]  # [text, confidence]
            
            # Calculate position
            x_min = min([pt[0] for pt in box])
            y_min = min([pt[1] for pt in box])
            
            lines_with_pos.append({
                'text': text_info[0],
                'x': x_min,
                'y': y_min,
                'confidence': text_info[1],
                'box': box
            })
    
    # Sort by Y position, then by X position
    lines_with_pos.sort(key=lambda x: (x['y'], x['x']))
    
    # Group into lines and detect structure
    structured_lines = []
    current_y = None
    current_line_items = []
    
    for item in lines_with_pos:
        # If Y position is similar (same line), group together
        if current_y is None or abs(item['y'] - current_y) < 20:
            current_line_items.append(item)
            if current_y is None:
                current_y = item['y']
        else:
            # New line, process previous line
            if current_line_items:
                line_text = format_line_with_layout(current_line_items, image_width)
                structured_lines.append(line_text)
            
            # Start new line
            current_line_items = [item]
            current_y = item['y']
    
    # Process last line
    if current_line_items:
        line_text = format_line_with_layout(current_line_items, image_width)
        structured_lines.append(line_text)
    
    return '\n'.join(structured_lines)

def format_line_with_layout(line_items, image_width):
    """
    Format một dòng với layout preservation
    Detect tables, spacing, alignment
    """
    if not line_items:
        return ""
    
    # Sort items by X position
    line_items.sort(key=lambda x: x['x'])
    
    # Detect table structure (multiple columns)
    if len(line_items) > 1:
        # Calculate spacing between items
        spacings = []
        for i in range(len(line_items) - 1):
            current_end = max([pt[0] for pt in line_items[i]['box']])
            next_start = line_items[i + 1]['x']
            spacing = next_start - current_end
            spacings.append(spacing)
        
        # If consistent spacing > threshold, it's a table
        avg_spacing = sum(spacings) / len(spacings) if spacings else 0
        if avg_spacing > 50:  # Table-like structure
            # Format as table with consistent spacing
            texts = [item['text'] for item in line_items]
            # Use tab or multiple spaces to preserve columns
            return '\t'.join(texts)  # Tab for table columns
    
    # Regular line - join texts
    texts = [item['text'] for item in line_items]
    return ' '.join(texts)

def preserve_spacing_in_text(text: str) -> str:
    """
    Preserve spacing và alignment trong text
    """
    lines = text.split('\n')
    preserved_lines = []
    
    for line in lines:
        # Preserve leading spaces (indentation)
        leading_spaces = len(line) - len(line.lstrip())
        
        # Preserve tabs (table columns)
        if '\t' in line:
            preserved_lines.append(line)
            continue
        
        # Preserve multiple spaces (alignment)
        if re.search(r'  {2,}', line):
            preserved_lines.append(line)
            continue
        
        # Regular line
        preserved_lines.append(line)
    
    return '\n'.join(preserved_lines)

