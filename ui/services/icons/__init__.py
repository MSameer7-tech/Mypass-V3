"""
Hybrid Website Icon Pipeline for MyPass.
Provides 3-layer cached, asynchronous, multi-provider favicon resolution with instant monogram fallback.
"""
from ui.services.icons.pipeline import IconPipeline

__all__ = ["IconPipeline"]
