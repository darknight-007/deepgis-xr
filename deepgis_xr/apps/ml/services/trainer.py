from typing import Optional
import os
import json
from pathlib import Path

import torch
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

from deepgis_xr.apps.core.models import CategoryType, TiledGISLabel
from deepgis_xr.apps.core.utils.utils import preprocess_image


class DeepGISTrainer:
    """Training service for DeepGIS models"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._get_model()
        
    def _get_model(self):
        """Get base model"""
        num_classes = len(CategoryType.objects.all()) + 1  # +1 for background
        
        # Load pre-trained model
        model = maskrcnn_resnet50_fpn(pretrained=True)
        
        # Replace the pre-trained head with a new one
        in_features = model.roi_heads.box_predictor.cls_score.in_features
        model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
        
        # Replace mask predictor
        in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
        hidden_layer = 256
        model.roi_heads.mask_predictor = MaskRCNNPredictor(
            in_features_mask,
            hidden_layer,
            num_classes
        )
        
        model.to(self.device)
        return model
        
    def prepare_dataset(self):
        """Prepare training dataset"""
        # Get all TiledGISLabel objects
        labels = TiledGISLabel.objects.all()
        categories = CategoryType.objects.all()
        
        # Create dataset directory
        dataset_dir = os.path.join(self.output_dir, "datasets")
        os.makedirs(dataset_dir, exist_ok=True)
        
        # Prepare dataset
        dataset = []
        for label in labels:
            # Load and preprocess image
            image = preprocess_image(label.parent_raster.read())
            
            # Prepare target
            target = {
                'boxes': torch.tensor([
                    [
                        label.southwest_lng,
                        label.southwest_lat,
                        label.northeast_lng,
                        label.northeast_lat
                    ]
                ], dtype=torch.float32),
                'labels': torch.tensor([label.category.id], dtype=torch.int64),
                'masks': torch.tensor(label.label_json["geometry"]["coordinates"], dtype=torch.uint8)
            }
            
            dataset.append((image, target))
            
        return dataset
        
    def train(self) -> str:
        """Train the model"""
        # Prepare dataset
        dataset = self.prepare_dataset()
        
        # Training parameters
        params = [p for p in self.model.parameters() if p.requires_grad]
        optimizer = torch.optim.SGD(params, lr=0.005, momentum=0.9, weight_decay=0.0005)
        
        # Training loop
        num_epochs = 10
        for epoch in range(num_epochs):
            self.model.train()
            
            for images, targets in dataset:
                images = images.to(self.device)
                targets = [{k: v.to(self.device) for k, v in t.items()} for t in [targets]]
                
                loss_dict = self.model(images, targets)
                losses = sum(loss for loss in loss_dict.values())
                
                optimizer.zero_grad()
                losses.backward()
                optimizer.step()
        
        # Save model
        model_path = os.path.join(self.output_dir, 'model.pth')
        torch.save(self.model.state_dict(), model_path)
        
        return self.output_dir 