import os
import sys
import logging
import argparse
from pptx_to_png import convert_pptx_to_png

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_pptx_files(directory):
    """Find all PowerPoint files in a directory"""
    pptx_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.pptx'):
                pptx_files.append(os.path.join(root, file))
    return pptx_files

def main():
    """Test the PowerPoint to PNG converter"""
    parser = argparse.ArgumentParser(description="Test PowerPoint to PNG converter")
    parser.add_argument("-f", "--file", help="Path to a specific PowerPoint file")
    parser.add_argument("-d", "--directory", help="Directory to search for PowerPoint files")
    parser.add_argument("-o", "--output-dir", help="Output directory for PNG files")
    parser.add_argument("--dpi", type=int, default=300, help="DPI for output images (default: 300)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Find PowerPoint files
    pptx_files = []
    if args.file:
        if os.path.exists(args.file) and args.file.lower().endswith('.pptx'):
            pptx_files.append(args.file)
        else:
            logger.error(f"Invalid PowerPoint file: {args.file}")
            sys.exit(1)
    elif args.directory:
        if os.path.isdir(args.directory):
            pptx_files = find_pptx_files(args.directory)
            if not pptx_files:
                logger.error(f"No PowerPoint files found in directory: {args.directory}")
                sys.exit(1)
        else:
            logger.error(f"Invalid directory: {args.directory}")
            sys.exit(1)
    else:
        # Default: search in media/templates directory
        templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "media", "templates")
        if os.path.isdir(templates_dir):
            pptx_files = find_pptx_files(templates_dir)
            if not pptx_files:
                logger.error(f"No PowerPoint files found in default directory: {templates_dir}")
                sys.exit(1)
        else:
            logger.error(f"Default directory not found: {templates_dir}")
            sys.exit(1)
    
    # Process each PowerPoint file
    for pptx_file in pptx_files:
        logger.info(f"Processing: {pptx_file}")
        try:
            output_dir = args.output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "png_output")
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert PowerPoint to PNG
            png_paths = convert_pptx_to_png(pptx_file, output_dir, args.dpi)
            logger.info(f"Successfully converted {len(png_paths)} slides to PNG")
            
            # Print the paths of the first few PNG files
            for i, png_path in enumerate(png_paths[:3]):
                logger.info(f"Slide {i+1}: {png_path}")
            if len(png_paths) > 3:
                logger.info(f"... and {len(png_paths) - 3} more slides")
        except Exception as e:
            logger.error(f"Error converting {pptx_file}: {e}")

if __name__ == "__main__":
    main() 