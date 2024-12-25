from django.http import HttpResponse, JsonResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from deepgis_xr.apps.core.models import Image, CategoryType, ImageLabel


class BaseView:
    """Base class for all web views"""
    template_name = None
    
    @classmethod
    def get_context(cls, request, **kwargs):
        """Get base context data"""
        return {
            'categories': {
                cat.category_name: str(cat.color) 
                for cat in CategoryType.objects.all()
            }
        }
    
    @classmethod
    def render(cls, request, **kwargs):
        """Render template with context"""
        context = cls.get_context(request, **kwargs)
        return render(request, cls.template_name, context)


class IndexView(BaseView):
    """Main landing page"""
    template_name = 'web/index.html'
    
    @classmethod
    @login_required
    def as_view(cls, request):
        return cls.render(request)


class LabelView(BaseView):
    """Image labeling interface"""
    template_name = 'web/label.html'
    
    @classmethod
    def get_context(cls, request, **kwargs):
        context = super().get_context(request, **kwargs)
        latest_images = Image.objects.all()
        
        if latest_images:
            context.update({
                'latest_image_list': latest_images,
                'selected_image': latest_images[0],
            })
        
        return context
    
    @classmethod
    @login_required 
    def as_view(cls, request):
        return cls.render(request)


class MapLabelView(BaseView):
    """Map-based labeling interface"""
    template_name = 'web/map_label.html'
    
    @classmethod
    @login_required
    def as_view(cls, request):
        return cls.render(request)


class ViewLabelView(BaseView):
    """View existing labels"""
    template_name = 'web/view_label.html'
    
    @classmethod
    @login_required
    def as_view(cls, request):
        return cls.render(request)


class ResultsView(BaseView):
    """View labeling results"""
    template_name = 'web/results.html'
    
    @classmethod
    @login_required
    def as_view(cls, request):
        return cls.render(request)


# URL routing
index = IndexView.as_view
label = LabelView.as_view
map_label = MapLabelView.as_view
view_label = ViewLabelView.as_view
results = ResultsView.as_view 