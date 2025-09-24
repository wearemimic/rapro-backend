import os
import sys
import logging
from pptx_to_png import convert_pptx_to_png

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Test PowerPoint to PNG converter in Docker container"""
    # Find a PowerPoint file
    templates_dir = os.path.join('media', 'templates')
    if not os.path.exists(templates_dir):
        logger.error(f"Templates directory not found: {templates_dir}")
        sys.exit(1)
    
    # Find all PowerPoint files
    pptx_files = []
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.lower().endswith('.pptx'):
                pptx_files.append(os.path.join(root, file))
    
    if not pptx_files:
        logger.error(f"No PowerPoint files found in {templates_dir}")
        sys.exit(1)
    
    # Use the first PowerPoint file
    pptx_file = pptx_files[0]
    logger.info(f"Using PowerPoint file: {pptx_file}")
    
    # Create output directory
    output_dir = os.path.join('media', 'thumbnails')
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Convert PowerPoint to PNG
        logger.info(f"Converting {pptx_file} to PNG images...")
        png_paths = convert_pptx_to_png(pptx_file, output_dir, dpi=300)
        
        logger.info(f"Successfully converted {len(png_paths)} slides to PNG")
        
        # Print the paths of the first few PNG files
        for i, png_path in enumerate(png_paths[:3]):
            logger.info(f"Slide {i+1}: {png_path}")
        if len(png_paths) > 3:
            logger.info(f"... and {len(png_paths) - 3} more slides")
    except Exception as e:
        logger.error(f"Error converting PowerPoint file: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 