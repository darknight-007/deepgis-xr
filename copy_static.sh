#!/bin/bash

# Create necessary directories
mkdir -p static/rock-tiles
mkdir -p data/raster_tiles

# Copy files from source to static directory
cp /mnt/2tbc2000mx500ssd/deepgis/deepgis_rocks/static-root/C3_mask_v3.tif static/
cp /mnt/2tbc2000mx500ssd/deepgis/deepgis_rocks/static-root/C3.tif static/
cp /mnt/2tbc2000mx500ssd/deepgis/deepgis_rocks/static-root/pb-rock.stl static/
cp /mnt/2tbc2000mx500ssd/deepgis/deepgis_rocks/rocks-coord-list.csv static/

# Copy rock tiles
cp -r /mnt/2tbc2000mx500ssd/deepgis/deepgis_rocks_static_serving_nginx/static/rock-tiles/raw/* static/rock-tiles/

# Set permissions
chmod -R 755 static/ 