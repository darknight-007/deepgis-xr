from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from deepgis_xr.apps.core.models import (
    Color, CategoryType, Image, ImageSourceType,
    Labeler, ImageWindow, ImageLabel, CategoryLabel
)


class ColorTests(TestCase):
    """Test Color model"""
    
    def test_color_creation(self):
        """Test creating a color"""
        color = Color.objects.create(red=255, green=128, blue=0)
        self.assertEqual(str(color), "rgb(255, 128, 0)")
        
    def test_color_validation(self):
        """Test color value validation"""
        with self.assertRaises(ValidationError):
            Color.objects.create(red=256, green=0, blue=0)


class CategoryTypeTests(TestCase):
    """Test CategoryType model"""
    
    def setUp(self):
        self.color = Color.objects.create(red=255, green=0, blue=0)
        
    def test_category_creation(self):
        """Test creating a category"""
        category = CategoryType.objects.create(
            category_name="test",
            color=self.color,
            label_type="P"
        )
        self.assertEqual(str(category), "Category: test")


class ImageTests(TestCase):
    """Test Image model"""
    
    def setUp(self):
        self.source = ImageSourceType.objects.create(description="test")
        
    def test_image_creation(self):
        """Test creating an image"""
        image = Image.objects.create(
            name="test.jpg",
            path="/test/",
            description="Test image",
            source=self.source,
            width=1920,
            height=1080
        )
        self.assertEqual(str(image), "Image: test.jpg")


class LabelerTests(TestCase):
    """Test Labeler model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        
    def test_labeler_creation(self):
        """Test creating a labeler"""
        labeler = Labeler.objects.create(user=self.user)
        self.assertEqual(str(labeler), str(self.user))


class ImageLabelTests(TestCase):
    """Test ImageLabel model"""
    
    def setUp(self):
        self.source = ImageSourceType.objects.create(description="test")
        self.image = Image.objects.create(
            name="test.jpg",
            path="/test/",
            source=self.source
        )
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.labeler = Labeler.objects.create(user=self.user)
        self.window = ImageWindow.objects.create(
            x=0, y=0, width=100, height=100
        )
        
    def test_image_label_creation(self):
        """Test creating an image label"""
        label = ImageLabel.objects.create(
            image=self.image,
            combined_label_shapes="<svg></svg>",
            labeler=self.labeler,
            window=self.window,
            time_taken=60
        )
        self.assertIsNotNone(label.pub_date)
        self.assertEqual(label.time_taken, 60) 