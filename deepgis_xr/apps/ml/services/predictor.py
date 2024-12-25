from typing import Dict, Any, Optional
import torch
import numpy as np
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.structures import BoxMode
from detectron2.utils.visualizer import Visualizer

from deepgis_xr.apps.core.models import CategoryType

class BasePredictor:
    """Base class for all predictors"""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = self._load_model()
        
    def _load_model(self):
        """Load the ML model - to be implemented by subclasses"""
        raise NotImplementedError
        
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """Run prediction on image - to be implemented by subclasses"""
        raise NotImplementedError


class MaskRCNNPredictor(BasePredictor):
    """Mask R-CNN implementation"""
    
    def _load_model(self):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(CategoryType.objects.all())
        
        if self.model_path and os.path.exists(self.model_path):
            cfg.MODEL.WEIGHTS = self.model_path
        else:
            cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.confidence_threshold
        return DefaultPredictor(cfg)
    
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """Run inference on an image"""
        outputs = self.model(image)
        
        # Convert outputs to CPU numpy arrays
        instances = outputs["instances"].to("cpu")
        return {
            "instances": instances,
            "pred_boxes": instances.pred_boxes.tensor.numpy(),
            "scores": instances.scores.numpy(),
            "pred_classes": instances.pred_classes.numpy(),
            "pred_masks": instances.pred_masks.numpy()
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
            category_idx = predictions["pred_classes"][i]
            
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