"""
Text to Image Converter for Copy Protection
Renders text as images to prevent copying while maintaining readability.
"""

import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import textwrap
from typing import Optional, Tuple

def text_to_image(
    text: str, 
    width: int = 1000,  # Increased width for better readability
    font_size: int = 26,  # Much larger font size
    line_height: int = 36,  # Increased line height
    padding: int = 30,  # More padding
    bg_color: Tuple[int, int, int] = (255, 255, 255),
    text_color: Tuple[int, int, int] = (0, 0, 0),
    font_path: Optional[str] = None
) -> Image.Image:
    """
    Convert text to an image for copy protection.
    
    Args:
        text: Text to render
        width: Image width in pixels
        font_size: Font size
        line_height: Line spacing
        padding: Padding around text
        bg_color: Background color (RGB)
        text_color: Text color (RGB)
        font_path: Optional path to custom font
    
    Returns:
        PIL Image object
    """
    # Try to use a larger system font for better readability
    try:
        # Try to use a TrueType font with the specified size
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        try:
            # Fallback to Arial if available
            font = ImageFont.truetype("Arial", font_size)
        except:
            # Use default font but try to scale it
            font = ImageFont.load_default()
    
    # Wrap text to fit width - adjust for larger font
    chars_per_line = int(width / (font_size * 0.6))  # Better approximation for character width
    wrapper = textwrap.TextWrapper(width=chars_per_line)
    lines = []
    for paragraph in text.split('\n'):
        if paragraph.strip():
            wrapped = wrapper.wrap(paragraph)
            lines.extend(wrapped)
        else:
            lines.append('')  # Preserve empty lines
    
    # Calculate image height
    height = (len(lines) * line_height) + (2 * padding)
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text
    y_position = padding
    for line in lines:
        draw.text((padding, y_position), line, fill=text_color, font=font)
        y_position += line_height
    
    return img


def render_protected_text(
    text: str,
    title: Optional[str] = None,
    width: int = 800,  # Increased width
    font_size: int = 28,  # Much larger font
    show_warning: bool = True
) -> None:
    """
    Render text as a protected image in Streamlit.
    
    Args:
        text: Text to display
        title: Optional title
        width: Image width
        font_size: Font size
        show_warning: Whether to show copy protection warning
    """
    if title:
        st.markdown(f"### {title}")
    
    # Convert text to image
    img = text_to_image(text, width=width, font_size=font_size)
    
    # Display image
    st.image(img, use_container_width=True)
    
    if show_warning:
        st.caption("📝 This content is protected and cannot be copied.")


def render_protected_markdown(
    markdown_text: str,
    width: int = 800,  # Increased width
    font_size: int = 28  # Much larger font
) -> None:
    """
    Render markdown-formatted text as protected images.
    Splits by sections for better rendering.
    
    Args:
        markdown_text: Markdown formatted text
        width: Image width
        font_size: Font size
    """
    # Split by major sections (###)
    sections = markdown_text.split('###')
    
    for i, section in enumerate(sections):
        if section.strip():
            # Extract title if it's the first line
            lines = section.strip().split('\n', 1)
            if i > 0 and len(lines) > 0:  # Skip first empty split
                title = lines[0].strip()
                content = lines[1] if len(lines) > 1 else ""
                
                # Clean up markdown formatting for display
                content = content.replace('**', '')  # Remove bold markers
                content = content.replace('*', '')   # Remove italic markers
                content = content.replace('- ', '• ')  # Convert to bullet points
                
                # Create section image
                if title:
                    st.markdown(f"### {title}")
                if content:
                    img = text_to_image(content.strip(), width=width, font_size=font_size)
                    st.image(img, use_container_width=True)
            elif i == 0 and section.strip():
                # Handle content before first ###
                content = section.strip()
                content = content.replace('**', '')
                content = content.replace('*', '')
                content = content.replace('- ', '• ')
                img = text_to_image(content, width=width, font_size=font_size)
                st.image(img, use_container_width=True)


def create_protected_expander(
    label: str,
    content: str,
    width: int = 800,  
    font_size: int = 28  # Much larger font
) -> None:
    """
    Create an expander with protected content.
    
    Args:
        label: Expander label
        content: Content to protect
        width: Image width
        font_size: Font size
    """
    with st.expander(label):
        # Clean up content
        clean_content = content.replace('**', '').replace('*', '').replace('- ', '• ')
        img = text_to_image(clean_content.strip(), width=width, font_size=font_size)
        st.image(img, use_container_width=True)
        st.caption("📝 This content is protected and cannot be copied.")


def encode_image_base64(img: Image.Image) -> str:
    """
    Encode PIL Image to base64 string for HTML embedding.
    
    Args:
        img: PIL Image object
    
    Returns:
        Base64 encoded string
    """
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str


def render_protected_html(
    text: str,
    width: int = 800,  # Increased width
    font_size: int = 28  # Much larger font
) -> None:
    """
    Render text as protected HTML with additional JavaScript protection.
    
    Args:
        text: Text to protect
        width: Image width
        font_size: Font size
    """
    # Create image
    img = text_to_image(text, width=width, font_size=font_size)
    img_base64 = encode_image_base64(img)
    
    # Create protected HTML (using triple quotes to avoid f-string issues with JavaScript)
    protected_html = f"""
    <div class="protected-content" style="position: relative;">
        <img src="data:image/png;base64,{img_base64}" 
             style="width: 100%; user-select: none; -webkit-user-select: none; -moz-user-select: none; -ms-user-select: none;"
             draggable="false"
             oncontextmenu="return false;"
             onselectstart="return false;"
             onmousedown="return false;">
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1000; background: transparent;"
             oncontextmenu="return false;"
             onselectstart="return false;"
             onmousedown="return false;">
        </div>
    </div>
    <script>
    document.addEventListener('DOMContentLoaded', function() {{
        document.querySelectorAll('.protected-content').forEach(function(elem) {{
            elem.addEventListener('contextmenu', function(e) {{
                e.preventDefault();
                return false;
            }});
            elem.addEventListener('selectstart', function(e) {{
                e.preventDefault();
                return false;
            }});
            elem.addEventListener('dragstart', function(e) {{
                e.preventDefault();
                return false;
            }});
        }});
        
        document.addEventListener('keydown', function(e) {{
            if ((e.ctrlKey || e.metaKey) && (e.keyCode == 65 || e.keyCode == 67 || e.keyCode == 88)) {{
                e.preventDefault();
                return false;
            }}
        }});
    }});
    </script>
    """
    
    st.markdown(protected_html, unsafe_allow_html=True)
