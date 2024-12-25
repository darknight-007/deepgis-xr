from typing import Optional
import os
import json
from pathlib import Path

import torch
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data import DatasetCatalog, MetadataCatalog
from detectron2.evaluation import COCOEvaluator

from deepgis_xr.apps.core.models import CategoryType, TiledGISLabel


class DeepGISTrainer:
    """Training service for DeepGIS models"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.cfg = self._get_config()
        
    def _get_config(self):
        """Get base detectron2 config"""
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"))
        
        # Set basic training params
        cfg.DATASETS.TRAIN = ("deepgis_train",)
        cfg.DATASETS.TEST = ()
        cfg.DATALOADER.NUM_WORKERS = 2
        cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml")
        
        # Training parameters
        cfg.SOLVER.IMS_PER_BATCH = 2
        cfg.SOLVER.BASE_LR = 0.00025
        cfg.SOLVER.MAX_ITER = 1000
        cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(CategoryType.objects.all())
        
        # Output directory
        cfg.OUTPUT_DIR = self.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        
        return cfg
        
    def prepare_dataset(self):
        """Prepare training dataset in COCO format"""
        # Get all TiledGISLabel objects
        labels = TiledGISLabel.objects.all()
        categories = CategoryType.objects.all()
        
        # Create COCO format dataset
        dataset = {
            "images": [],
            "annotations": [],
            "categories": []
        }
        
        # Add categories
        for idx, cat in enumerate(categories):
            dataset["categories"].append({
                "id": idx + 1,
                "name": cat.category_name,
                "supercategory": "object"
            })
        
        # Add images and annotations
        image_id = 1
        ann_id = 1
        
        for label in labels:
            # Add image
            dataset["images"].append({
                "id": image_id,
                "file_name": label.parent_raster.path,
                "height": label.parent_raster.height,
                "width": label.parent_raster.width
            })
            
            # Add annotation
            dataset["annotations"].append({
                "id": ann_id,
                "image_id": image_id,
                "category_id": label.category.id,
                "segmentation": label.label_json["geometry"]["coordinates"],
                "bbox": [
                    label.southwest_lng,
                    label.southwest_lat,
                    label.northeast_lng - label.southwest_lng,
                    label.northeast_lat - label.southwest_lat
                ],
                "area": label.geometry.area,
                "iscrowd": 0
            })
            
            image_id += 1
            ann_id += 1
        
        # Save dataset
        dataset_dir = os.path.join(self.output_dir, "datasets")
        os.makedirs(dataset_dir, exist_ok=True)
        
        dataset_path = os.path.join(dataset_dir, "deepgis_train.json")
        with open(dataset_path, "w") as f:
            json.dump(dataset, f)
            
        # Register dataset
        DatasetCatalog.register(
            "deepgis_train",
            lambda: dataset
        )
        
        MetadataCatalog.get("deepgis_train").set(
            thing_classes=[cat.category_name for cat in categories]
        )
        
    def train(self) -> str:
        """Train the model"""
        # Prepare dataset
        self.prepare_dataset()
        
        # Initialize trainer
        trainer = DefaultTrainer(self.cfg)
        trainer.resume_or_load(resume=False)
        
        # Start training
        trainer.train()
        
        return self.output_dir 