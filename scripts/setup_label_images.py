#!/usr/bin/env python
"""
Setup script to create the directory structure and download sample images for the label app.
"""
import os
import sys
import shutil
import requests
from pathlib import Path
import urllib.parse

# List of sample image URLs to download
SAMPLE_IMAGES = [
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/Lake_Bondhus_Norway_2862.jpg/1200px-Lake_Bondhus_Norway_2862.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/24701-nature-natural-beauty.jpg/1200px-24701-nature-natural-beauty.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Altja_j%C3%B5gi_Lahemaal.jpg/1200px-Altja_j%C3%B5gi_Lahemaal.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Biandintz_eta_zaldiak_-_modified2.jpg/1200px-Biandintz_eta_zaldiak_-_modified2.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Taktsang_Palphug_Monastery_in_2019.jpg/1200px-Taktsang_Palphug_Monastery_in_2019.jpg"
]

def main():
    # Define paths
    script_dir = Path(__file__).resolve().parent
    project_dir = script_dir.parent
    static_dir = project_dir / "static"
    images_dir = static_dir / "images" / "label-set" / "navagunjara-ortho-set"
    
    # Create directory structure
    try:
        images_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {images_dir}")
    except Exception as e:
        print(f"Error creating directory: {e}")
        return 1
    
    # Download sample images
    for i, url in enumerate(SAMPLE_IMAGES, 1):
        try:
            filename = f"image_{i}.jpg"
            output_path = images_dir / filename
            
            # Skip if file already exists
            if output_path.exists():
                print(f"Image already exists: {filename}")
                continue
            
            print(f"Downloading {url} to {filename}...")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            print(f"Successfully downloaded: {filename}")
            
        except Exception as e:
            print(f"Error downloading {url}: {e}")
    
    print("\nSetup complete!")
    print(f"Image directory: {images_dir}")
    print("\nTo import these images to the database, run:")
    print(f"python manage.py import_images --directory {images_dir} --source 'Sample Images' --path-prefix 'https://deepgis.org/static/images/label-set/navagunjara-ortho-set/'")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 