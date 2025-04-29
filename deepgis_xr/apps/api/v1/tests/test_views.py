import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from deepgis_xr.apps.core.models import (
    RasterImage, CategoryType, TiledGISLabel, Labeler
)

User = get_user_model()


class BaseAPITest(TestCase):
    """Base class for API tests"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.login(username='testuser', password='testpass')


class PredictionAPITests(BaseAPITest):
    """Test prediction endpoints"""
    
    def setUp(self):
        super().setUp()
        self.raster = RasterImage.objects.create(
            name="test.tif",
            path="/test/test.tif",
            attribution="test",
            min_zoom=0,
            max_zoom=20
        )
        
    def test_predict_tile(self):
        """Test tile prediction"""
        url = reverse('predict_tile')
        data = {
            'bounds': [0, 0, 100, 100],
            'raster_id': self.raster.id,
            'confidence_threshold': 0.5
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'success')
        
    def test_predict_tile_invalid_bounds(self):
        """Test prediction with invalid bounds"""
        url = reverse('predict_tile')
        data = {
            'bounds': [0, 0],  # Invalid bounds
            'raster_id': self.raster.id
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TrainingAPITests(BaseAPITest):
    """Test training endpoints"""
    
    def setUp(self):
        super().setUp()
        self.user.is_staff = True
        self.user.save()
        
    def test_start_training(self):
        """Test starting model training"""
        url = reverse('start_training')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'success')
        self.assertIn('task_id', response.json())
        
    def test_start_training_unauthorized(self):
        """Test training without staff permissions"""
        self.user.is_staff = False
        self.user.save()
        
        url = reverse('start_training')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_training_status(self):
        """Test getting training status"""
        # First start training
        start_url = reverse('start_training')
        start_response = self.client.post(start_url)
        task_id = start_response.json()['task_id']
        
        # Then check status
        status_url = reverse('get_training_status', args=[task_id])
        response = self.client.get(status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('state', response.json()) 