import os
import sys
import glob
import logging
from PIL import Image
from core.pptx_utils import check_external_tools, convert_pptx_to_pdf, extract_images_from_pdf, get_dominant_color

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(message)s')

def main():
    """Test if external tools are available for PowerPoint conversion"""
    print("Checking for external tools...")
    tools = check_external_tools()
    
    if tools["libreoffice"]:
        print(f"LibreOffice: Available at {tools['libreoffice']}")
    else:
        print("LibreOffice: Not found")
    
    if tools["poppler"]:
        print("pdf2image/poppler: Available")
    else:
        print("pdf2image/poppler: Not available")
    
    # Exit if tools are not available
    if not tools["libreoffice"] or not tools["poppler"]:
        print("\nNot all tools are available. Please install:")
        if not tools["libreoffice"]:
            print("- LibreOffice (https://www.libreoffice.org/)")
            print("  On macOS: brew install libreoffice")
        if not tools["poppler"]:
            print("- pdf2image and poppler (pip install pdf2image)")
            print("  On macOS: brew install poppler")
        return
    
    print("\nBoth tools are available! Testing conversion...")
    
    # Find a PPTX file to test
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media", "templates")
    print(f"Looking for PPTX files in {templates_dir}...")
    
    pptx_files = []
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".pptx"):
                pptx_files.append(os.path.join(root, file))
    
    if not pptx_files:
        print("No PPTX files found in the templates directory.")
        return
    
    # Use the first PPTX file found
    test_pptx = pptx_files[0]
    print(f"Found PPTX file: {test_pptx}")
    
    # Create a temporary output directory
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Test conversion
    print(f"Converting {test_pptx} to PDF...")
    pdf_path = convert_pptx_to_pdf(test_pptx, output_dir)
    
    if pdf_path:
        print(f"Successfully converted to PDF: {pdf_path}")
        
        print("Extracting images from PDF...")
        images = extract_images_from_pdf(pdf_path)
        
        if images:
            print(f"Successfully extracted {len(images)} images from PDF")
            
            # Save the first few images as thumbnails
            for i, img in enumerate(images[:3]):
                thumbnail_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"slide_{i+1}_thumbnail_libreoffice.png")
                img.save(thumbnail_path)
                print(f"Saved thumbnail: {thumbnail_path}")
                
                # For slide 2, analyze the dominant colors
                if i == 1:  # 0-indexed, so 1 is slide 2
                    dominant_color = get_dominant_color(img)
                    print(f"\nSlide 2 dominant color: RGB{dominant_color}")
                    
                    # Check if it's blue (for the hexagon slide)
                    r, g, b = dominant_color
                    if r < 50 and g > 50 and b > 150:
                        print("Detected blue background on slide 2 (hexagon slide)")
                    
                    # Sample some pixels to check colors
                    width, height = img.size
                    sample_points = [
                        (50, 50), 
                        (width - 50, 50),
                        (50, height - 50),
                        (width - 50, height - 50),
                        (width // 2, height // 2)
                    ]
                    
                    print("\nColor sampling for slide 2:")
                    for x, y in sample_points:
                        pixel = img.getpixel((x, y))
                        print(f"Pixel at ({x}, {y}): {pixel}")
        else:
            print("Failed to extract images from PDF")
    else:
        print("Failed to convert PPTX to PDF.")
        
        # Try to check if soffice is executable
        if tools["libreoffice"]:
            import stat
            mode = os.stat(tools["libreoffice"]).st_mode
            is_executable = bool(mode & stat.S_IXUSR)
            print(f"Is LibreOffice executable? {is_executable}")
            
            # Try running LibreOffice with --version
            import subprocess
            try:
                print("Testing LibreOffice with --version command...")
                result = subprocess.run([tools["libreoffice"], "--version"], 
                                       capture_output=True, text=True, timeout=10)
                print(f"Return code: {result.returncode}")
                print(f"Output: {result.stdout}")
                if result.stderr:
                    print(f"Error: {result.stderr}")
            except Exception as e:
                print(f"Error running LibreOffice: {str(e)}")

if __name__ == "__main__":
    main() 