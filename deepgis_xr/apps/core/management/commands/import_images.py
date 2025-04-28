import os
import sys
import glob
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from deepgis_xr.apps.core.models import Image, ImageSourceType, CategoryType
from PIL import Image as PILImage

class Command(BaseCommand):
    help = 'Import images from a directory and sync with the database'

    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, required=True,
                            help='Directory containing images to import')
        parser.add_argument('--source', type=str, default='import',
                            help='Image source description (default: import)')
        parser.add_argument('--path-prefix', type=str, default='',
                            help='Prefix to add to image paths in the database')
        parser.add_argument('--clean', action='store_true',
                            help='Remove database entries for images not found in directory')
        parser.add_argument('--categories', nargs='+', default=['Buildings', 'Roads', 'Vegetation', 'Water Bodies'],
                            help='Categories to assign to imported images')

    def handle(self, *args, **options):
        directory = options['directory']
        source_desc = options['source']
        path_prefix = options['path_prefix']
        clean = options['clean']
        category_names = options['categories']

        # Validate directory
        if not os.path.isdir(directory):
            raise CommandError(f'Directory "{directory}" does not exist')

        self.stdout.write(self.style.SUCCESS(f'Importing images from {directory}'))

        # Get or create source type
        source, created = ImageSourceType.objects.get_or_create(description=source_desc)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created new image source: {source_desc}'))

        # Get or create categories
        categories = []
        for cat_name in category_names:
            category, created = CategoryType.objects.get_or_create(category_name=cat_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created new category: {cat_name}'))
            categories.append(category)

        # Find all images in directory
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tif', '*.tiff']
        files = []
        for ext in image_extensions:
            files.extend(glob.glob(os.path.join(directory, ext)))
            files.extend(glob.glob(os.path.join(directory, ext.upper())))
        
        if not files:
            self.stdout.write(self.style.WARNING(f'No image files found in {directory}'))
            return

        # Create a set of existing image paths for quick lookup
        existing_images = set()
        if clean:
            for image in Image.objects.filter(source=source):
                # Store the full path (prefix + name) for comparison
                existing_images.add(os.path.join(image.path, image.name))

        # Track imported and skipped images
        imported_count = 0
        skipped_count = 0
        
        # Import images
        for file_path in files:
            file_name = os.path.basename(file_path)
            relative_path = path_prefix or os.path.dirname(os.path.relpath(file_path, directory))
            
            # Check if image already exists
            try:
                image = Image.objects.get(name=file_name, path=relative_path)
                skipped_count += 1
                existing_images.discard(os.path.join(relative_path, file_name))
            except Image.DoesNotExist:
                # Get image dimensions
                try:
                    with PILImage.open(file_path) as img:
                        width, height = img.size
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {file_path}: {str(e)}'))
                    continue

                # Create new image record
                image = Image.objects.create(
                    name=file_name,
                    path=relative_path,
                    description=f'Imported from {directory}',
                    source=source,
                    width=width,
                    height=height
                )
                
                # Add categories
                for category in categories:
                    image.categories.add(category)
                
                self.stdout.write(f'Imported: {file_name} ({width}x{height})')
                imported_count += 1

        # Clean up database if requested
        if clean and existing_images:
            for path in existing_images:
                path_dir, filename = os.path.split(path)
                try:
                    image = Image.objects.get(name=filename, path=path_dir)
                    image.delete()
                    self.stdout.write(f'Removed: {filename} (no longer in directory)')
                except Image.DoesNotExist:
                    pass  # Should not happen, but just in case
            
            self.stdout.write(self.style.SUCCESS(f'Removed {len(existing_images)} images no longer in directory'))

        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {imported_count} imported, {skipped_count} skipped'
        )) 