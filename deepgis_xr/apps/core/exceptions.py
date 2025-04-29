class DeepGISException(Exception):
    """Base exception for DeepGIS application"""
    default_message = "An error occurred"
    
    def __init__(self, message=None, *args, **kwargs):
        self.message = message or self.default_message
        super().__init__(self.message, *args, **kwargs)


class ModelNotFoundError(DeepGISException):
    """Raised when ML model is not found"""
    default_message = "Model not found"


class InvalidModelError(DeepGISException):
    """Raised when ML model is invalid"""
    default_message = "Invalid model format or configuration"


class PredictionError(DeepGISException):
    """Raised when prediction fails"""
    default_message = "Failed to generate prediction"


class TrainingError(DeepGISException):
    """Raised when model training fails"""
    default_message = "Model training failed"


class DatasetError(DeepGISException):
    """Raised when there are dataset issues"""
    default_message = "Dataset error"


class ValidationError(DeepGISException):
    """Raised for data validation errors"""
    default_message = "Validation failed"


class AuthorizationError(DeepGISException):
    """Raised for authorization issues"""
    default_message = "Not authorized"


class ConfigurationError(DeepGISException):
    """Raised for configuration issues"""
    default_message = "Configuration error"


class ResourceNotFoundError(DeepGISException):
    """Raised when a resource is not found"""
    default_message = "Resource not found"


class ServiceError(DeepGISException):
    """Raised for external service errors"""
    default_message = "Service error" 