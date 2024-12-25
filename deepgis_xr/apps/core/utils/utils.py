import torch
import numpy as np
import rasterio
import albumentations as A
from typing import List, Union, Tuple

def preprocess_image(
    image: Union[np.ndarray, torch.Tensor],
    target_size: Tuple[int, int] = (512, 512)
) -> torch.Tensor:
    """Preprocess image for model input."""
    # Create transform pipeline
    transform = A.Compose([
        A.Resize(target_size[0], target_size[1]),
        A.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
    
    # Convert to correct format if needed
    if isinstance(image, torch.Tensor):
        image = image.numpy()
    
    # Ensure correct shape (C, H, W)
    if image.shape[0] not in [1, 3]:
        image = np.moveaxis(image, -1, 0)
    
    # Apply transforms
    transformed = transform(image=image)
    image = transformed['image']
    
    # Convert to tensor
    image = torch.from_numpy(image).float()
    if len(image.shape) == 3:
        image = image.unsqueeze(0)
    
    return image

def postprocess_predictions(
    predictions: torch.Tensor,
    confidence_threshold: float = 0.5
) -> List[np.ndarray]:
    """Convert model predictions to binary masks."""
    # Move predictions to CPU and convert to numpy
    predictions = predictions.cpu().numpy()
    
    # Apply threshold
    binary_masks = (predictions > confidence_threshold).astype(np.uint8)
    
    # Split into list of individual masks if batch
    if len(binary_masks.shape) == 4:
        return [mask for mask in binary_masks]
    return [binary_masks]

def load_raster(
    path: str,
    bands: List[int] = None
) -> Tuple[np.ndarray, rasterio.transform.Affine, dict]:
    """Load raster data and return image array, transform, and metadata."""
    with rasterio.open(path) as src:
        if bands:
            image = src.read(bands)
        else:
            image = src.read()
        transform = src.transform
        meta = src.meta
    return image, transform, meta

def save_predictions(
    predictions: np.ndarray,
    transform: rasterio.transform.Affine,
    output_path: str,
    metadata: dict
) -> None:
    """Save predictions as a raster file."""
    metadata.update({
        'count': 1,
        'dtype': 'uint8',
        'driver': 'GTiff'
    })
    
    with rasterio.open(output_path, 'w', **metadata) as dst:
        dst.write(predictions.astype('uint8'), 1)

def create_tiles(
    image: np.ndarray,
    tile_size: int = 256,
    overlap: int = 32
) -> List[Tuple[np.ndarray, Tuple[int, int]]]:
    """Split large image into tiles with overlap."""
    tiles = []
    positions = []
    
    height, width = image.shape[1:] if len(image.shape) > 2 else image.shape
    
    for y in range(0, height, tile_size - overlap):
        for x in range(0, width, tile_size - overlap):
            x1 = min(x + tile_size, width)
            y1 = min(y + tile_size, height)
            x0 = max(0, x1 - tile_size)
            y0 = max(0, y1 - tile_size)
            
            tile = image[:, y0:y1, x0:x1] if len(image.shape) > 2 else image[y0:y1, x0:x1]
            tiles.append(tile)
            positions.append((x0, y0))
    
    return tiles, positions

def stitch_tiles(
    tiles: List[np.ndarray],
    positions: List[Tuple[int, int]],
    image_size: Tuple[int, int],
    tile_size: int = 256,
    overlap: int = 32
) -> np.ndarray:
    """Stitch tiles back together, handling overlapping regions."""
    height, width = image_size
    result = np.zeros((height, width), dtype=np.float32)
    weights = np.zeros((height, width), dtype=np.float32)
    
    for tile, (x, y) in zip(tiles, positions):
        x1 = min(x + tile_size, width)
        y1 = min(y + tile_size, height)
        
        # Create weight matrix for blending
        weight = np.ones_like(tile)
        if overlap > 0:
            weight = create_weight_matrix(tile.shape, overlap)
        
        result[y:y1, x:x1] += tile * weight
        weights[y:y1, x:x1] += weight
    
    # Normalize by weights to blend overlapping regions
    return result / (weights + 1e-6) 