from typing import Dict, Any, Optional, List
import torch
import numpy as np
import os
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.transforms import functional as F
from shapely.geometry import Polygon
from shapely.geometry import mapping
from skimage import measure

from deepgis_xr.apps.core.models import CategoryType

class BasePredictor:
    """Base class for all predictors"""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = self._load_model()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
    def _load_model(self):
        """Load the ML model - to be implemented by subclasses"""
        raise NotImplementedError
        
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """Run prediction on image - to be implemented by subclasses"""
        raise NotImplementedError


class MaskRCNNPredictor(BasePredictor):
    """Mask R-CNN implementation using torchvision"""
    
    def _load_model(self):
        num_classes = len(CategoryType.objects.all()) + 1  # +1 for background
        model = maskrcnn_resnet50_fpn(pretrained=True)
        
        # Modify the classifier to match our number of classes
        in_features = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
        
        # Load custom weights if available
        if self.model_path and os.path.exists(self.model_path):
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        
        model.to(self.device)
        model.eval()
        return model
    
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """Run inference on an image"""
        # Convert numpy array to tensor
        image_tensor = F.to_tensor(image).to(self.device)
        
        with torch.no_grad():
            predictions = self.model([image_tensor])[0]
        
        # Filter predictions based on confidence threshold
        mask = predictions['scores'] >= self.confidence_threshold
        
        return {
            "pred_boxes": predictions['boxes'][mask].cpu().numpy(),
            "scores": predictions['scores'][mask].cpu().numpy(),
            "pred_classes": predictions['labels'][mask].cpu().numpy(),
            "pred_masks": predictions['masks'][mask].squeeze(1).cpu().numpy()
        }
    
    def predictions_to_geojson(self, 
                             predictions: Dict[str, Any],
                             transform: Any,
                             categories: List[CategoryType]) -> Dict[str, Any]:
        """Convert predictions to GeoJSON format"""
        features = []
        
        for i in range(len(predictions["pred_boxes"])):
            mask = predictions["pred_masks"][i]
            score = predictions["scores"][i]
            category_idx = predictions["pred_classes"][i] - 1  # Subtract 1 as class 0 is background
            
            # Convert binary mask to polygon
            contours = measure.find_contours(mask, 0.5)
            for contour in contours:
                # Convert to geographic coordinates
                coords = transform * contour
                polygon = Polygon(coords)
                
                feature = {
                    "type": "Feature",
                    "geometry": mapping(polygon),
                    "properties": {
                        "category": categories[category_idx].category_name,
                        "confidence": float(score)
                    }
                }
                features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features
        } 