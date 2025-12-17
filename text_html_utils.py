"""
Utility functions để tách text và HTML
- Extract text thuần từ HTML (strip HTML tags)
- Convert text thành HTML
"""

import re


def extract_text_from_html(html_content):
    """
    Extract text thuần từ HTML (strip HTML tags)
    
    Args:
        html_content: HTML string hoặc text có HTML tags
        
    Returns:
        Plain text (không có HTML tags)
    """
    if not html_content:
        return ''
    
    # Nếu không có HTML tags, return như cũ
    if not ('<' in html_content and '>' in html_content):
        return html_content
    
    # Strip HTML tags
    # Remove script và style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Decode HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")
    text = text.replace('&apos;', "'")
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces -> single space
    text = re.sub(r'\n\s*\n', '\n', text)  # Multiple newlines -> single newline
    
    return text.strip()


def text_to_html_paragraphs(text):
    """
    Convert text thành HTML với format giống PDF (backward compatibility)
    """
    return text_to_html_paragraphs_with_alignment(text, [])

def text_to_html_paragraphs_with_alignment(text, lines_with_alignment=None):
    """
    Convert text thành HTML với format giống PDF và alignment
    - Giữ nguyên xuống dòng
    - Giữ nguyên spacing
    - Áp dụng text-align (left/center/right) dựa trên alignment info
    - Giữ nguyên whitespace
    
    Args:
        text: Plain text
        lines_with_alignment: List of dicts với {'text': str, 'alignment': 'left'|'center'|'right'}
        
    Returns:
        HTML string với format giống PDF và alignment
    """
    if not text:
        return ''
    
    lines = text.split('\n')
    html_lines = []
    
    # Tạo map từ text -> alignment nếu có
    alignment_map = {}
    if lines_with_alignment:
        for line_info in lines_with_alignment:
            line_text = line_info.get('text', '')
            alignment = line_info.get('alignment', 'left')
            alignment_map[line_text] = alignment
    
    for i, line in enumerate(lines):
        # Escape HTML entities trước
        line_escaped = line.replace('&', '&amp;')
        line_escaped = line_escaped.replace('<', '&lt;')
        line_escaped = line_escaped.replace('>', '&gt;')
        
        # Tìm alignment cho line này
        alignment = 'left'  # default
        if line in alignment_map:
            alignment = alignment_map[line]
        elif lines_with_alignment and i < len(lines_with_alignment):
            # Fallback: dùng index
            alignment = lines_with_alignment[i].get('alignment', 'left')
        
        if line.strip():
            # Line có text - giữ nguyên whitespace và áp dụng alignment
            html_lines.append(f'<p style="white-space: pre-wrap; margin: 5px 0; text-align: {alignment};">{line_escaped}</p>')
        else:
            # Empty line -> <p>&nbsp;</p> để giữ spacing
            html_lines.append('<p style="margin: 5px 0;">&nbsp;</p>')
    
    return '\n'.join(html_lines)


def split_text_and_html(content):
    """
    Split content thành text thuần và HTML
    - Nếu content có HTML tags -> extract text thuần và giữ HTML
    - Nếu content là text thuần -> giữ text và convert sang HTML
    
    Args:
        content: Content có thể là text hoặc HTML
        
    Returns:
        Tuple (plain_text, html)
    """
    if not content:
        return '', ''
    
    # Check if content có HTML tags
    has_html_tags = '<' in content and '>' in content and re.search(r'<[^>]+>', content)
    
    if has_html_tags:
        # Content là HTML -> extract text thuần
        plain_text = extract_text_from_html(content)
        html = content
    else:
        # Content là text thuần -> convert sang HTML
        plain_text = content
        html = text_to_html_paragraphs(content)
    
    return plain_text, html

