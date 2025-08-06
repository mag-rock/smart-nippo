"""Initialize models and resolve forward references."""

def init_models():
    """Initialize models and resolve forward references."""
    from .template import Template
    from .report import Report
    
    # Rebuild models to resolve forward references
    Report.model_rebuild()

# Call initialization
init_models()