from django.urls import path

from .views import prediction, training

urlpatterns = [
    # Prediction endpoints
    path('predict/tile/', 
         prediction.predict_tile, 
         name='predict_tile'),
    
    path('predict/save/', 
         prediction.save_predictions, 
         name='save_predictions'),
    
    # Training endpoints  
    path('train/start/',
         training.start_training,
         name='start_training'),
    
    path('train/status/<str:task_id>/',
         training.get_training_status,
         name='get_training_status'),
] 