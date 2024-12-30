from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import os

from deepgis_xr.apps.core.models import Image, CategoryType, ImageLabel


class BaseView(TemplateView):
    """Base class for all web views"""
    
    def get_context_data(self, **kwargs):
        """Get base context data"""
        context = super().get_context_data(**kwargs)
        context['categories'] = {
            cat.category_name: str(cat.color) 
            for cat in CategoryType.objects.all()
        }
        return context


class IndexView(BaseView):
    """Main landing page"""
    template_name = 'web/index.html'


class LabelView(BaseView):
    """Image labeling interface"""
    template_name = 'web/label.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        latest_images = Image.objects.all()
        
        if latest_images:
            context.update({
                'latest_image_list': latest_images,
                'selected_image': latest_images[0],
            })
        
        return context


class MapLabelView(BaseView):
    """Map-based labeling interface"""
    template_name = 'web/map_label.html'


class ViewLabelView(BaseView):
    """View existing labels"""
    template_name = 'web/view_label.html'


class ResultsView(BaseView):
    """View labeling results"""
    template_name = 'web/results.html'


# URL routing
index = IndexView.as_view()
label = LabelView.as_view()
map_label = MapLabelView.as_view()
view_label = ViewLabelView.as_view()
results = ResultsView.as_view()


@csrf_exempt
def get_available_layers(request):
    """Return available tile layers"""
    try:
        layers = [
            {
                'name': 'Raw Rock Data (C3)',
                'url': 'http://localhost:8091/data/c3/{z}/{x}/{y}.png',
                'attribution': 'DeepGIS Rock Data'
            },
            {
                'name': 'Colorized Rock Data',
                'url': 'http://localhost:8091/data/c3_color/{z}/{x}/{y}.png',
                'attribution': 'DeepGIS Rock Data'
            }
        ]
        return JsonResponse({
            'status': 'success',
            'layers': layers
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def get_category_info(request):
    """Return available categories"""
    try:
        categories = {
            'Rock': {
                'color': '#FF0000',
                'id': 1
            },
            'Vegetation': {
                'color': '#00FF00',
                'id': 2
            },
            'Shadow': {
                'color': '#0000FF',
                'id': 3
            }
        }
        return JsonResponse(categories)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def get_new_image(request):
    """Return a new image for labeling"""
    try:
        return JsonResponse({
            'status': 'success',
            'image_url': '/static/images/sample.jpg',
            'image_id': '123'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


@csrf_exempt
def save_label(request):
    """Save a label"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # TODO: Save label data to database
            return JsonResponse({
                'status': 'success'
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405)


@csrf_exempt
def create_category(request):
    """Create a new category"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            if not name:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Category name is required'
                }, status=400)
            
            # TODO: Save category to database
            import random
            color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
            
            return JsonResponse({
                'status': 'success',
                'category': {
                    'name': name,
                    'color': color,
                    'id': len(CategoryType.objects.all()) + 1
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON'
            }, status=400)
    return JsonResponse({
        'status': 'error',
        'message': 'Method not allowed'
    }, status=405) 