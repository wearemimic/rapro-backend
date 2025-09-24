import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from pptx_to_png import convert_pptx_to_png

class Command(BaseCommand):
    help = 'Convert PowerPoint files to PNG images'

    def add_arguments(self, parser):
        parser.add_argument('pptx_file', help='Path to the PowerPoint file')
        parser.add_argument('-o', '--output-dir', help='Output directory for PNG files')
        parser.add_argument('-d', '--dpi', type=int, default=300, help='DPI for output images (default: 300)')

    def handle(self, *args, **options):
        pptx_file = options['pptx_file']
        output_dir = options['output_dir']
        dpi = options['dpi']

        if not os.path.exists(pptx_file):
            self.stderr.write(self.style.ERROR(f"PowerPoint file not found: {pptx_file}"))
            return

        if not output_dir:
            output_dir = os.path.join(settings.MEDIA_ROOT, 'png_output')
            os.makedirs(output_dir, exist_ok=True)

        try:
            self.stdout.write(f"Converting {pptx_file} to PNG images...")
            png_paths = convert_pptx_to_png(pptx_file, output_dir, dpi)
            self.stdout.write(self.style.SUCCESS(f"Successfully converted {len(png_paths)} slides to PNG"))
            
            # Print the paths of the first few PNG files
            for i, png_path in enumerate(png_paths[:3]):
                self.stdout.write(f"Slide {i+1}: {png_path}")
            if len(png_paths) > 3:
                self.stdout.write(f"... and {len(png_paths) - 3} more slides")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error converting PowerPoint file: {str(e)}")) 