import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_libreoffice():
    """Find the LibreOffice executable path"""
    libreoffice_path = None
    
    # Check for LibreOffice on Linux
    linux_paths = [
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
        "/usr/lib/libreoffice/program/soffice",
        "/usr/local/bin/soffice"
    ]
    
    # Check each path
    for path in linux_paths:
        if os.path.exists(path):
            logger.info(f"Found LibreOffice at: {path}")
            libreoffice_path = path
            break
    
    # If not found, try using which command
    if not libreoffice_path:
        try:
            libreoffice_path = subprocess.check_output(["which", "soffice"]).decode().strip()
            logger.info(f"Found LibreOffice using 'which' command: {libreoffice_path}")
        except (subprocess.SubprocessError, FileNotFoundError):
            try:
                libreoffice_path = subprocess.check_output(["which", "libreoffice"]).decode().strip()
                logger.info(f"Found LibreOffice using 'which libreoffice' command: {libreoffice_path}")
            except (subprocess.SubprocessError, FileNotFoundError):
                pass
    
    # Log the result
    if libreoffice_path:
        logger.info(f"Using LibreOffice at: {libreoffice_path}")
        
        # Try to run LibreOffice with --version
        try:
            version = subprocess.check_output([libreoffice_path, "--version"], stderr=subprocess.STDOUT).decode().strip()
            logger.info(f"LibreOffice version: {version}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting LibreOffice version: {e}")
            logger.error(f"Output: {e.output.decode() if hasattr(e, 'output') else 'No output'}")
    else:
        logger.error("LibreOffice not found. Please install LibreOffice.")
        
        # List all directories in /usr/bin that contain 'office' or 'libre'
        try:
            if os.path.exists('/usr/bin'):
                bin_files = os.listdir('/usr/bin')
                libre_files = [f for f in bin_files if 'libre' in f or 'office' in f]
                if libre_files:
                    logger.info(f"Found possible LibreOffice executables in /usr/bin: {libre_files}")
        except Exception as e:
            logger.error(f"Error listing /usr/bin: {e}")
    
    return libreoffice_path

def check_poppler():
    """Check if poppler-utils is installed"""
    try:
        version = subprocess.check_output(["pdftoppm", "-v"], stderr=subprocess.STDOUT).decode().strip()
        logger.info(f"Poppler version: {version}")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Poppler-utils not found. Please install poppler-utils.")
        return False

if __name__ == "__main__":
    logger.info("Checking for LibreOffice...")
    libreoffice_path = find_libreoffice()
    
    logger.info("Checking for Poppler...")
    poppler_installed = check_poppler()
    
    # Print system information
    logger.info(f"System: {sys.platform}")
    logger.info(f"Python version: {sys.version}")
    
    # List all files in /usr/bin
    try:
        if os.path.exists('/usr/bin'):
            bin_files = os.listdir('/usr/bin')
            logger.info(f"Files in /usr/bin: {len(bin_files)} files")
    except Exception as e:
        logger.error(f"Error listing /usr/bin: {e}")
    
    # Summary
    if libreoffice_path and poppler_installed:
        logger.info("All dependencies are installed!")
    else:
        logger.error("Some dependencies are missing!") 