"""
OCR with Layout Preservation
Giữ layout (bảng, cột, spacing, alignment) khi OCR và sửa chính tả
"""

import re
from typing import List, Dict, Tuple, Optional

class LayoutPreserver:
    """Preserve layout information during OCR and text correction"""
    
    @staticmethod
    def detect_table_structure(text: str) -> Dict:
        """Detect table-like structure trong text"""
        lines = text.split('\n')
        table_lines = []
        is_table = False
        
        for line in lines:
            # Detect table (multiple spaces/tabs, consistent spacing)
            if '\t' in line or re.search(r'  {2,}', line):
                is_table = True
                table_lines.append(line)
            elif is_table and not line.strip():
                # Empty line might separate table from text
                break
        
        return {
            'is_table': is_table,
            'table_lines': table_lines,
            'separator': '---TABLE---'
        }
    
    @staticmethod
    def preserve_line_breaks(text: str) -> str:
        """Preserve line breaks và paragraph structure"""
        # Giữ multiple newlines (paragraph breaks)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text
    
    @staticmethod
    def add_layout_markers(text: str) -> str:
        """
        Thêm markers để giữ layout khi gửi cho GPT
        Format: Special markers để GPT biết đâu là table, list, etc.
        """
        lines = text.split('\n')
        marked_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                marked_lines.append('')
                continue
            
            # Detect và mark tables
            if '\t' in line or re.search(r'  {2,}', line):
                # Table row - giữ nguyên spacing
                marked_lines.append(f"[TABLE_ROW]{line}[/TABLE_ROW]")
                continue
            
            # Detect numbered list
            if re.match(r'^\d+[\.\)]\s+', stripped):
                marked_lines.append(f"[LIST]{line}[/LIST]")
                continue
            
            # Detect bullet list
            if re.match(r'^[-•*]\s+', stripped):
                marked_lines.append(f"[BULLET]{line}[/BULLET]")
                continue
            
            # Regular paragraph
            marked_lines.append(line)
        
        return '\n'.join(marked_lines)
    
    @staticmethod
    def remove_layout_markers(text: str) -> str:
        """Remove layout markers sau khi GPT trả về"""
        text = re.sub(r'\[TABLE_ROW\](.*?)\[/TABLE_ROW\]', r'\1', text)
        text = re.sub(r'\[LIST\](.*?)\[/LIST\]', r'\1', text)
        text = re.sub(r'\[BULLET\](.*?)\[/BULLET\]', r'\1', text)
        return text

def structure_text_with_layout(text: str) -> str:
    """
    Structure text để giữ layout khi gửi cho GPT
    """
    preserver = LayoutPreserver()
    
    # Detect và mark layout
    marked_text = preserver.add_layout_markers(text)
    
    # Preserve line breaks
    marked_text = preserver.preserve_line_breaks(marked_text)
    
    return marked_text

def restore_layout_after_correction(original: str, corrected: str) -> str:
    """
    Restore layout từ original text sau khi GPT đã sửa chính tả
    """
    preserver = LayoutPreserver()
    
    # Remove markers
    corrected = preserver.remove_layout_markers(corrected)
    
    original_lines = original.split('\n')
    corrected_lines = corrected.split('\n')
    
    # Map structure từ original
    result_lines = []
    
    for i, orig_line in enumerate(original_lines):
        # Giữ leading spaces từ original
        leading_spaces = len(orig_line) - len(orig_line.lstrip())
        
        if i < len(corrected_lines):
            # Lấy corrected content nhưng giữ spacing
            corrected_content = corrected_lines[i].strip()
            result_lines.append(' ' * leading_spaces + corrected_content)
        else:
            # Giữ original line nếu không có trong corrected
            result_lines.append(orig_line)
    
    return '\n'.join(result_lines)
