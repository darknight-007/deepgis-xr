from rest_framework import serializers
from django.contrib.gis.geos import GEOSGeometry

from deepgis_xr.apps.core.models import (
    CategoryType, Image, ImageLabel, CategoryLabel,
    TiledGISLabel, RasterImage
)


class ColorSerializer(serializers.Serializer):
    """Color representation"""
    red = serializers.IntegerField(min_value=0, max_value=255)
    green = serializers.IntegerField(min_value=0, max_value=255)
    blue = serializers.IntegerField(min_value=0, max_value=255)


class CategoryTypeSerializer(serializers.ModelSerializer):
    """Category type serializer"""
    color = ColorSerializer()
    
    class Meta:
        model = CategoryType
        fields = ['id', 'category_name', 'color', 'label_type']


class ImageSerializer(serializers.ModelSerializer):
    """Image serializer"""
    categories = CategoryTypeSerializer(many=True, read_only=True)
    
    class Meta:
        model = Image
        fields = ['id', 'name', 'path', 'description', 'width', 'height', 'categories']


class ImageLabelSerializer(serializers.ModelSerializer):
    """Image label serializer"""
    image = ImageSerializer(source='parentImage', read_only=True)
    
    class Meta:
        model = ImageLabel
        fields = ['id', 'image', 'combined_label_shapes', 'pub_date', 'time_taken']


class CategoryLabelSerializer(serializers.ModelSerializer):
    """Category-specific label serializer"""
    category = CategoryTypeSerializer()
    parent = ImageLabelSerializer(source='parent_label')
    
    class Meta:
        model = CategoryLabel
        fields = ['id', 'category', 'label_shapes', 'parent']


class RasterImageSerializer(serializers.ModelSerializer):
    """Raster image serializer"""
    class Meta:
        model = RasterImage
        fields = ['id', 'name', 'path', 'attribution', 'min_zoom', 'max_zoom', 
                 'resolution', 'latitude', 'longitude']


class TiledGISLabelSerializer(serializers.ModelSerializer):
    """GIS label serializer"""
    category = CategoryTypeSerializer()
    parent_raster = RasterImageSerializer()
    
    class Meta:
        model = TiledGISLabel
        fields = ['id', 'northeast_lat', 'northeast_lng', 'southwest_lat', 
                 'southwest_lng', 'zoom_level', 'category', 'label_json',
                 'label_type', 'parent_raster', 'pub_date']
        
    def validate_label_json(self, value):
        """Validate GeoJSON format"""
        try:
            geometry = value.get('geometry', {})
            GEOSGeometry(str(geometry))
        except Exception as e:
            raise serializers.ValidationError(f"Invalid GeoJSON geometry: {str(e)}")
        return value


# Request/Response Serializers
class PredictionRequestSerializer(serializers.Serializer):
    """Prediction request parameters"""
    bounds = serializers.ListField(
        child=serializers.FloatField(),
        min_length=4,
        max_length=4
    )
    raster_id = serializers.IntegerField()
    model_path = serializers.CharField(required=False)
    confidence_threshold = serializers.FloatField(default=0.5)


class PredictionResponseSerializer(serializers.Serializer):
    """Prediction response format"""
    status = serializers.CharField()
    predictions = serializers.DictField()
    message = serializers.CharField(required=False)


class TrainingRequestSerializer(serializers.Serializer):
    """Training request parameters"""
    output_dir = serializers.CharField(required=False)
    

class TrainingResponseSerializer(serializers.Serializer):
    """Training response format"""
    status = serializers.CharField()
    message = serializers.CharField()
    task_id = serializers.CharField() 