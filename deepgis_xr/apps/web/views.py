from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render

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