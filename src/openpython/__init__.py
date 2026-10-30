"""Openpython: a lightweight AI code helper for IPython/Jupyter."""

from .assistant import OpenPythonError, generate_code
from .extension import load_ipython_extension, start

__all__ = ["OpenPythonError", "generate_code", "load_ipython_extension", "start"]
__version__ = "0.1.0"
