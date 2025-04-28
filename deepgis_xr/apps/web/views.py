from django.http import HttpResponse, JsonResponse, FileResponse
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import tempfile
import zipfile
import os
from shapely.geometry import shape
import fiona
import requests
from urllib.parse import urljoin

from deepgis_xr.apps.core.models import Image, CategoryType, ImageLabel, RasterImage


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
    """Get an image from the database for labeling, with support for navigation"""
    import random
    from deepgis_xr.apps.core.models import Image, CategoryType
    
    # Check if requesting a specific navigation direction
    direction = request.GET.get('direction', 'next')
    
    # Get all images from the database
    all_images = list(Image.objects.all())
    
    # If no images in database, return error response
    if not all_images:
        return JsonResponse({
            'success': False,
            'message': 'No images available in the database'
        })
    
    # Get the current image ID from session if it exists
    current_image_id = request.session.get('current_image_id', None)
    
    try:
        # Find the current image in the list
        current_index = -1
        if current_image_id is not None:
            for i, img in enumerate(all_images):
                if img.id == current_image_id:
                    current_index = i
                    break
        
        # Handle navigation based on direction
        if direction == 'prev' and current_index > 0:
            # Go to previous image
            current_index -= 1
        elif direction == 'next' and current_index < len(all_images) - 1:
            # Go to next image
            current_index += 1
        elif direction == 'next' and (current_index == -1 or current_index == len(all_images) - 1):
            # Start from beginning if at end or no current image
            current_index = 0
        elif direction == 'prev' and (current_index == -1):
            # Start from last image if no current image and going backwards
            current_index = len(all_images) - 1
        
        # Get the image at the current index
        image = all_images[current_index]
        
        # Save the current image ID in session
        request.session['current_image_id'] = image.id
        
        # Prepare image data for frontend
        image_name = image.name
        path = image.path
        
        # Ensure the path is a valid image URL, not just a directory
        # If the path doesn't contain a file extension, it might be a directory
        if not path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
            # Check if the path ends with a slash, remove it if it does
            if path.endswith('/'):
                path = path[:-1]
            
            # Append the image name as the filename if it has an extension
            if image_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')):
                path = f"{path}/{image_name}"
            else:
                # Default to a .jpg extension if no extension in the name
                path = f"{path}/{image_name}.jpg"
        
        # Ensure the URL has http/https prefix
        if not path.startswith(('http://', 'https://')):
            path = f"https://{path}" if not path.startswith('//') else f"https:{path}"
        
        # Process categories
        if image.categories.exists():
            categories = [cat.category_name for cat in image.categories.all()]
            colors = []
            shapes = []
            for cat in image.categories.all():
                if cat.color:
                    r, g, b = cat.color.red, cat.color.green, cat.color.blue
                    colors.append(f'#{r:02x}{g:02x}{b:02x}')
                else:
                    colors.append('#FF0000')  # Default red
                
                # Map label_type to shape
                if cat.label_type == 'C':
                    shapes.append('circle')
                elif cat.label_type == 'R':
                    shapes.append('rectangle')
                elif cat.label_type == 'P':
                    shapes.append('bezier')
                else:
                    shapes.append('circle')  # Default to circle
        else:
            # Default categories if none are associated with the image
            categories = ['Buildings', 'Roads', 'Vegetation', 'Water Bodies']
            shapes = ['circle', 'circle', 'circle', 'circle']
            colors = ['#FF0000', '#00FF00', '#00AA00', '#0000FF']
        
        # Return the image data
        return JsonResponse({
            'success': True,
            'image_name': image_name,
            'image_path': path,
            'categories': categories,
            'shapes': shapes,
            'colors': colors,
            'width': getattr(image, 'width', 996),
            'height': getattr(image, 'height', 996),
            'navigation': {
                'has_prev': current_index > 0,
                'has_next': current_index < len(all_images) - 1,
                'current_index': current_index + 1,
                'total_images': len(all_images)
            }
        })
        
    except Exception as e:
        # Log the error
        print(f"Error in get_new_image: {str(e)}")
        # Return error response
        return JsonResponse({
            'success': False,
            'message': f'Error loading image: {str(e)}'
        }, status=500)

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

@csrf_exempt
def save_labels(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Save the GeoJSON data to your database or file system
            # This is a simplified example - you'll want to add proper validation and error handling
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def export_shapefile(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create a temporary directory for the shapefile
            with tempfile.TemporaryDirectory() as tmpdir:
                # Define the schema based on your GeoJSON properties
                schema = {
                    'geometry': 'Polygon',
                    'properties': {'category': 'str', 'label_id': 'int'},
                }
                
                # Create a shapefile from the GeoJSON
                shp_path = f"{tmpdir}/labels.shp"
                with fiona.open(shp_path, 'w', 
                              driver='ESRI Shapefile',
                              crs='EPSG:4326',
                              schema=schema) as shp:
                    # Write each feature to the shapefile
                    for feature in data['features']:
                        shp.write({
                            'geometry': feature['geometry'],
                            'properties': feature['properties']
                        })
                
                # Create a ZIP file containing the shapefile components
                zip_path = f"{tmpdir}/labels.zip"
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for ext in ['.shp', '.shx', '.dbf', '.prj']:
                        filename = f"labels{ext}"
                        filepath = f"{tmpdir}/{filename}"
                        if os.path.exists(filepath):
                            zipf.write(filepath, filename)
                
                # Return the ZIP file
                return FileResponse(
                    open(zip_path, 'rb'),
                    content_type='application/zip',
                    as_attachment=True,
                    filename='labels.zip'
                )
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def get_raster_info(request):
    """Get information about available raster layers."""
    
    try:
        rasters = RasterImage.objects.all()
        raster_info = []
        
        for raster in rasters:
            raster_info.append({
                'name': raster.name,
                'path': raster.path,
                'attribution': raster.attribution,
                'minZoom': raster.min_zoom,
                'maxZoom': raster.max_zoom,
                'lat_lng': [raster.latitude, raster.longitude]
            })
        
        return JsonResponse({
            'status': 'success',
            'message': raster_info
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def get_tileserver_layers(request):
    """Get available layers from the tileserver."""
    
    # Configure tileserver URL - use local for development
    TILESERVER_URL = 'https://localhost:8091'
    
    try:
        # Fetch layers from tileserver
        response = requests.get(f'{TILESERVER_URL}/data.json', timeout=5)
        response.raise_for_status()  # Raise exception for non-200 status codes
        
        data = response.json()
        layers = {}
        
        for layer_id, info in data.items():
            if not isinstance(info, dict):
                continue
            
            # Basic layer info
            layer = {
                'id': layer_id,
                'name': info.get('name', layer_id),
                'type': 'vector' if info.get('format') == 'pbf' else 'raster'
            }
            
            # Handle tiles URL
            tiles = info.get('tiles', [])
            if tiles:
                tile_url = tiles[0]
                if tile_url.startswith('/'):
                    tile_url = urljoin(TILESERVER_URL, tile_url.lstrip('/'))
            else:
                # Construct default tile URL
                ext = 'pbf' if layer['type'] == 'vector' else 'png'
                tile_url = f'{TILESERVER_URL}/data/{layer_id}/{{z}}/{{x}}/{{y}}.{ext}'
            
            layer['url'] = tile_url
            
            # Add optional properties if they exist
            for prop in ['minzoom', 'maxzoom', 'bounds', 'center', 'attribution']:
                if prop in info:
                    layer[prop] = info[prop]
            
            layers[layer_id] = layer
        
        return JsonResponse({
            'status': 'success',
            'layers': layers,
            'tileserver': TILESERVER_URL
        })
        
    except requests.exceptions.RequestException as e:
        print(f'Tileserver error: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'message': 'Could not connect to tileserver'
        }, status=503)
    except Exception as e:
        print(f'Unexpected error: {str(e)}')
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@csrf_exempt
def get_all_images(request):
    """Get all images from the database."""
    try:
        images = Image.objects.all()
        image_list = []
        
        for image in images:
            image_data = {
                'id': image.id,
                'name': image.name,
                'path': image.path if image.path.startswith(('http://', 'https://')) else image.path + '/',
                'width': image.width,
                'height': image.height,
                'description': image.description
            }
            image_list.append(image_data)
        
        return JsonResponse({
            'success': True,
            'images': image_list
        })
    except Exception as e:
        print(f'Error in get_all_images: {str(e)}')
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500) 