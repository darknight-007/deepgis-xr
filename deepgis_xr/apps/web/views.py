from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from deepgis_xr.apps.core.models import Image, CategoryType, ImageLabel


class BaseView(LoginRequiredMixin, TemplateView):
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

def index(request):
    return render(request, 'web/index.html')

def label(request):
    return render(request, 'web/label.html')

def map_label(request):
    return render(request, 'web/map_label.html')

def view_label(request):
    return render(request, 'web/view_label.html')

def results(request):
    return render(request, 'web/results.html')

@csrf_exempt
def get_category_info(request):
    # Return categories in the format expected by the frontend
    categories = {
        'Buildings': {
            'color': '#FF0000',
            'id': 1
        },
        'Roads': {
            'color': '#00FF00',
            'id': 2
        },
        'Water Bodies': {
            'color': '#0000FF',
            'id': 3
        }
    }
    return JsonResponse(categories)

@csrf_exempt
def get_new_image(request):
    # For now, return a sample response
    response = {
        'status': 'success',
        'image_url': '/static/images/sample.jpg',
        'image_id': '123'
    }
    return JsonResponse(response)

@csrf_exempt
def save_label(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Here you would save the label data
            # For now, just return success
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def create_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('name')
            
            # Get existing categories
            categories = {
                'Buildings': {
                    'color': '#FF0000',
                    'id': 1
                },
                'Roads': {
                    'color': '#00FF00',
                    'id': 2
                },
                'Water Bodies': {
                    'color': '#0000FF',
                    'id': 3
                }
            }
            
            # Add new category with a random color
            import random
            color = '#{:06x}'.format(random.randint(0, 0xFFFFFF))
            categories[category_name] = {
                'color': color,
                'id': len(categories) + 1
            }
            
            return JsonResponse({'status': 'success', 'category': {
                'name': category_name,
                'color': color,
                'id': len(categories)
            }})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405) 