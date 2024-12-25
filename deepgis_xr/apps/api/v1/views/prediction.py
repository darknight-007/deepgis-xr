from typing import Dict, Any
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
import rasterio
from rasterio.windows import Window
from rasterio.transform import from_bounds

from deepgis_xr.apps.core.models import RasterImage, CategoryType, TiledGISLabel, Labeler
from deepgis_xr.apps.ml.services.predictor import MaskRCNNPredictor


@csrf_exempt
@require_POST
@login_required
def predict_tile(request) -> JsonResponse:
    """Run AI prediction on a tile"""
    try:
        data = json.loads(request.body)
        bounds = data.get('bounds')  # [minx, miny, maxx, maxy]
        raster_id = data.get('raster_id')
        model_path = data.get('model_path')
        confidence_threshold = float(data.get('confidence_threshold', 0.5))
        
        if not all([bounds, raster_id]):
            return JsonResponse({
                "status": "failure",
                "message": "Missing required parameters"
            }, status=400)
        
        # Get raster image
        raster = RasterImage.objects.get(id=raster_id)
        
        with rasterio.open(raster.path) as src:
            # Calculate window from bounds
            window = src.window(*bounds)
            transform = from_bounds(*bounds, window.width, window.height)
            
            # Read image data
            image = src.read(window=window)
            
            # Initialize predictor and run inference
            predictor = MaskRCNNPredictor(
                model_path=model_path,
                confidence_threshold=confidence_threshold
            )
            predictions = predictor.predict(image)
            
            # Convert predictions to GeoJSON
            categories = CategoryType.objects.all()
            geojson = predictor.predictions_to_geojson(
                predictions, 
                transform,
                categories
            )
            
            return JsonResponse({
                "status": "success",
                "predictions": geojson
            })
            
    except Exception as e:
        return JsonResponse({
            "status": "failure",
            "message": str(e)
        }, status=500)


@csrf_exempt
@require_POST
@login_required
def save_predictions(request) -> JsonResponse:
    """Save AI predictions as TiledGISLabels"""
    try:
        data = json.loads(request.body)
        predictions = data.get('predictions')
        raster_id = data.get('raster_id')
        
        if not all([predictions, raster_id]):
            return JsonResponse({
                "status": "failure",
                "message": "Missing required parameters"
            }, status=400)
        
        raster = RasterImage.objects.get(id=raster_id)
        labeler = Labeler.objects.get(user=request.user)
        
        # Create TiledGISLabel objects from predictions
        created_labels = []
        for feature in predictions['features']:
            category_name = feature['properties']['category']
            category = CategoryType.objects.get(category_name=category_name)
            
            label = TiledGISLabel.objects.create(
                parent_raster=raster,
                labeler=labeler,
                category=category,
                label_json=feature,
                geometry=GEOSGeometry(json.dumps(feature['geometry'])),
                northeast_lat=feature['bbox'][3],
                northeast_lng=feature['bbox'][2],
                southwest_lat=feature['bbox'][1],
                southwest_lng=feature['bbox'][0]
            )
            created_labels.append(label.id)
        
        return JsonResponse({
            "status": "success",
            "created_labels": created_labels
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "failure",
            "message": str(e)
        }, status=500) 