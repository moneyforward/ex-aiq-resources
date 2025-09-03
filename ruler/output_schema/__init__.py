"""
Output Schema Package for Expense Rule Validation

This package provides structured output schemas for expense rule validation,
including reason taxonomy and suggested fixes system.
"""

from .reason_processor import (
    ReasonProcessor,
    get_reason_processor,
    generate_fix,
    format_reasons
)

__version__ = "1.0.0"
__all__ = [
    "ReasonProcessor",
    "get_reason_processor", 
    "generate_fix",
    "format_reasons"
]
