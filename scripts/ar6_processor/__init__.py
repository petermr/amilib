"""
AR6 Incremental Processing System

A make-like system for processing AR6 IPCC components through transformation stages.
Skips already completed work and enables incremental processing.
"""

from scripts.ar6_processor.registry import ComponentRegistry
from scripts.ar6_processor.pipeline import AR6Pipeline
from scripts.ar6_processor.batch_processor import BatchProcessor

__all__ = ['ComponentRegistry', 'AR6Pipeline', 'BatchProcessor']





