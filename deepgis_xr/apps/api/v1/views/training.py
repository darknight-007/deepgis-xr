import os
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.conf import settings
from celery import shared_task

from deepgis_xr.apps.ml.services.trainer import DeepGISTrainer


@shared_task
def train_model_task(output_dir: str) -> str:
    """Celery task for training the model"""
    trainer = DeepGISTrainer(output_dir=output_dir)
    return trainer.train()


@csrf_exempt
@require_POST
@login_required
def start_training(request) -> JsonResponse:
    """Start model training"""
    if not request.user.is_staff:
        return JsonResponse({
            "status": "failure", 
            "message": "Unauthorized"
        }, status=401)
    
    # Create output directory for model
    output_dir = os.path.join(
        settings.MEDIA_ROOT, 
        'models', 
        f'model_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    )
    
    # Start async training task
    task = train_model_task.delay(output_dir)
    
    return JsonResponse({
        "status": "success",
        "message": "Training started",
        "task_id": task.id
    })


@csrf_exempt
@require_GET
@login_required
def get_training_status(request, task_id: str) -> JsonResponse:
    """Get status of training task"""
    task = train_model_task.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Training pending...'
        }
    elif task.state == 'SUCCESS':
        response = {
            'state': task.state,
            'output_dir': task.get()
        }
    else:
        response = {
            'state': task.state,
            'status': str(task.info)
        }
    
    return JsonResponse(response) 