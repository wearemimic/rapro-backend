"""
File Scanner Service for Security Validation
Provides basic virus scanning and malicious file detection
"""

import hashlib
import logging
import mimetypes
import re
import zipfile
import tarfile
from io import BytesIO
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)


class FileScannerService:
    """
    Service for scanning uploaded files for security threats
    """

    # Dangerous file extensions that could execute code
    DANGEROUS_EXTENSIONS = {
        '.exe', '.dll', '.bat', '.cmd', '.com', '.msi', '.scr', '.vbs',
        '.js', '.jar', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.run',
        '.sh', '.bash', '.ps1', '.psm1', '.reg', '.ink', '.lnk'
    }

    # Suspicious patterns that might indicate malware
    MALWARE_PATTERNS = [
        # Common malware signatures (hex patterns)
        b'\x4D\x5A',  # PE executable header
        b'\x7F\x45\x4C\x46',  # ELF executable header
        b'\xCA\xFE\xBA\xBE',  # Mach-O executable
        b'\xFE\xED\xFA\xCE',  # Mach-O executable (32-bit)
        b'\xCE\xFA\xED\xFE',  # Mach-O executable (little-endian)

        # JavaScript malware patterns
        b'eval(unescape',
        b'document.write(unescape',
        b'String.fromCharCode',
        b'ActiveXObject',
        b'WScript.Shell',

        # PHP malware patterns
        b'<?php @eval',
        b'<?php eval(',
        b'base64_decode',
        b'shell_exec',
        b'system(',
        b'passthru(',
        b'exec(',

        # PowerShell malware
        b'IEX(',
        b'Invoke-Expression',
        b'DownloadString',
        b'-EncodedCommand',

        # Common exploit patterns
        b'<script>alert',
        b'javascript:alert',
        b'onerror=',
        b'onclick=',
        b'<iframe',
    ]

    # Maximum file size for scanning (100MB)
    MAX_SCAN_SIZE = 100 * 1024 * 1024

    # Maximum nested archive depth to prevent zip bombs
    MAX_ARCHIVE_DEPTH = 3

    @classmethod
    def scan_file(cls, file_content, filename, content_type=None):
        """
        Scan a file for security threats

        Args:
            file_content: bytes content of the file
            filename: original filename
            content_type: MIME type of the file

        Returns:
            dict: {
                'safe': bool,
                'threats': list of threat descriptions,
                'file_hash': SHA256 hash of the file,
                'scan_details': dict with scan metadata
            }
        """
        threats = []
        scan_details = {
            'filename': filename,
            'size': len(file_content),
            'content_type': content_type or mimetypes.guess_type(filename)[0],
        }

        # Check file size
        if len(file_content) > cls.MAX_SCAN_SIZE:
            logger.warning(f"File {filename} exceeds maximum scan size")
            scan_details['size_exceeded'] = True

        # Calculate file hash
        file_hash = hashlib.sha256(file_content).hexdigest()
        scan_details['file_hash'] = file_hash

        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext in cls.DANGEROUS_EXTENSIONS:
            threats.append(f"Dangerous file extension: {file_ext}")

        # Check for executable headers
        if cls._contains_executable_header(file_content):
            threats.append("File contains executable code headers")

        # Check for malware patterns
        malware_found = cls._scan_for_malware_patterns(file_content)
        if malware_found:
            threats.extend(malware_found)

        # Check if it's an archive and scan contents
        if cls._is_archive(filename, content_type):
            archive_threats = cls._scan_archive(file_content, filename)
            threats.extend(archive_threats)

        # Check for embedded macros in Office documents
        if cls._is_office_document(filename, content_type):
            macro_threats = cls._check_office_macros(file_content)
            threats.extend(macro_threats)

        # Check for suspicious PDF content
        if cls._is_pdf(filename, content_type):
            pdf_threats = cls._check_pdf_threats(file_content)
            threats.extend(pdf_threats)

        # Log scanning results
        if threats:
            logger.warning(f"File {filename} failed security scan: {threats}")
        else:
            logger.info(f"File {filename} passed security scan")

        return {
            'safe': len(threats) == 0,
            'threats': threats,
            'file_hash': file_hash,
            'scan_details': scan_details
        }

    @classmethod
    def _contains_executable_header(cls, content):
        """Check if file contains executable headers"""
        if len(content) < 4:
            return False

        # Check for common executable headers
        headers = [
            b'\x4D\x5A',  # PE/DOS executable
            b'\x7F\x45\x4C\x46',  # ELF
            b'\xCA\xFE\xBA\xBE',  # Mach-O
            b'\xFE\xED\xFA',  # Mach-O
            b'\xCE\xFA\xED\xFE',  # Mach-O
            b'#!/bin/',  # Shell script
            b'#! /bin/',  # Shell script with space
        ]

        for header in headers:
            if content[:len(header)] == header:
                return True

        return False

    @classmethod
    def _scan_for_malware_patterns(cls, content):
        """Scan content for known malware patterns"""
        threats = []

        # Limit scanning to first 1MB for performance
        scan_content = content[:1024*1024]

        for pattern in cls.MALWARE_PATTERNS:
            if pattern in scan_content:
                # Don't reveal the exact pattern for security
                threats.append("Suspicious code pattern detected")
                break

        return threats

    @classmethod
    def _is_archive(cls, filename, content_type):
        """Check if file is an archive"""
        archive_extensions = {'.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'}
        archive_types = {
            'application/zip', 'application/x-zip-compressed',
            'application/x-tar', 'application/gzip',
            'application/x-bzip2', 'application/x-7z-compressed',
            'application/x-rar-compressed'
        }

        ext = Path(filename).suffix.lower()
        return ext in archive_extensions or content_type in archive_types

    @classmethod
    def _scan_archive(cls, content, filename, depth=0):
        """Scan archive contents for threats"""
        threats = []

        if depth > cls.MAX_ARCHIVE_DEPTH:
            threats.append("Archive nesting depth exceeded (possible zip bomb)")
            return threats

        try:
            # Try to open as ZIP
            if filename.lower().endswith('.zip'):
                with zipfile.ZipFile(BytesIO(content)) as zf:
                    # Check for zip bomb
                    total_size = sum(info.file_size for info in zf.infolist())
                    if total_size > 1024 * 1024 * 1024:  # 1GB uncompressed
                        threats.append("Archive expands to excessive size (possible zip bomb)")
                        return threats

                    # Check each file in archive
                    for info in zf.infolist():
                        if Path(info.filename).suffix.lower() in cls.DANGEROUS_EXTENSIONS:
                            threats.append(f"Archive contains dangerous file: {info.filename}")

            # Try to open as TAR
            elif any(filename.lower().endswith(ext) for ext in ['.tar', '.tar.gz', '.tgz', '.tar.bz2']):
                with tarfile.open(fileobj=BytesIO(content)) as tf:
                    for member in tf.getmembers():
                        if Path(member.name).suffix.lower() in cls.DANGEROUS_EXTENSIONS:
                            threats.append(f"Archive contains dangerous file: {member.name}")

        except Exception as e:
            logger.debug(f"Could not scan archive {filename}: {e}")

        return threats

    @classmethod
    def _is_office_document(cls, filename, content_type):
        """Check if file is an Office document"""
        office_extensions = {
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.docm', '.xlsm', '.pptm'  # Macro-enabled
        }
        office_types = {
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }

        ext = Path(filename).suffix.lower()
        return ext in office_extensions or content_type in office_types

    @classmethod
    def _check_office_macros(cls, content):
        """Check Office documents for malicious macros"""
        threats = []

        # Check for macro-enabled file signatures
        if b'vbaProject.bin' in content:
            threats.append("Document contains VBA macros")

        # Check for auto-execution macro names
        dangerous_macro_names = [
            b'AutoOpen', b'AutoExec', b'AutoStart', b'AutoClose',
            b'Document_Open', b'Workbook_Open'
        ]

        for name in dangerous_macro_names:
            if name in content:
                threats.append("Document contains auto-execution macros")
                break

        return threats

    @classmethod
    def _is_pdf(cls, filename, content_type):
        """Check if file is a PDF"""
        return (filename.lower().endswith('.pdf') or
                content_type == 'application/pdf')

    @classmethod
    def _check_pdf_threats(cls, content):
        """Check PDF for embedded threats"""
        threats = []

        # Check for JavaScript in PDF
        if b'/JavaScript' in content or b'/JS' in content:
            threats.append("PDF contains embedded JavaScript")

        # Check for embedded files
        if b'/EmbeddedFile' in content:
            threats.append("PDF contains embedded files")

        # Check for launch actions
        if b'/Launch' in content:
            threats.append("PDF contains launch actions")

        # Check for suspicious form actions
        if b'/SubmitForm' in content or b'/ImportData' in content:
            threats.append("PDF contains form submission actions")

        return threats

    @classmethod
    def quarantine_file(cls, file_content, filename, threats):
        """
        Move dangerous file to quarantine

        In production, this would move the file to a secure quarantine location
        for manual review
        """
        logger.error(f"File {filename} quarantined due to threats: {threats}")

        # In production, you would:
        # 1. Move file to secure quarantine storage
        # 2. Log the incident with full details
        # 3. Notify security team
        # 4. Create audit trail

        # For now, just log the incident
        quarantine_info = {
            'filename': filename,
            'file_hash': hashlib.sha256(file_content).hexdigest(),
            'threats': threats,
            'quarantined_at': str(datetime.now()),
        }

        logger.error(f"QUARANTINE: {quarantine_info}")

        return quarantine_info


# Import datetime for quarantine timestamp
from datetime import datetime


def scan_uploaded_file(file_obj, filename=None):
    """
    Convenience function to scan an uploaded file

    Args:
        file_obj: Django UploadedFile object
        filename: Optional override for filename

    Returns:
        dict: Scan results
    """
    filename = filename or file_obj.name
    content_type = getattr(file_obj, 'content_type', None)

    # Read file content
    file_obj.seek(0)
    content = file_obj.read()
    file_obj.seek(0)  # Reset for further processing

    # Scan the file
    return FileScannerService.scan_file(content, filename, content_type)