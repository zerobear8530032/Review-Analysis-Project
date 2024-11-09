# __init__.py

from .invalidurlException import InvalidURLException
from .insufficientDataException import InsufficientDataException 
from .unabletoparseException import UnableToParseException

# Optionally, define the package’s `__all__` to specify what is imported with a wildcard (*) import.
__all__ = ["InvalidURLException", "InsufficientDataException","UnableToParseException"]
