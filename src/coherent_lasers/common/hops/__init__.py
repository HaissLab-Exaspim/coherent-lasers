"""
HOPS DLL Utilities Package

This package contains utilities and drivers for coherent lasers that use CohrHOPS DLL files.

Modules:
- manager: Contains the HOPSManager class for managing HOPS devices as a singleton.
- device: Contains the HOPSDevice class for interacting with HOPS DLL files.

Setup:
1. Download the required DLL files from the release assets on GitHub.
2. Place the DLL files in the 'dll' directory within this package.
"""

import ctypes
import logging
import os
import platform
import sys
from ctypes.util import find_library


# Ensure is windows
if not (sys.platform.startswith("win") and platform.machine().endswith("64")):
    raise OSError("This package only supports 64-bit Windows systems.")

# Setup logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

DLL_DIR = os.path.dirname(__file__)

# Add the DLL directory to the DLL search path
os.add_dll_directory(DLL_DIR)

# Add the DLL directory to the system PATH
os.environ["PATH"] = DLL_DIR + os.pathsep + os.environ["PATH"]

# Check for required DLLs using ctypes.util.find_library
REQUIRED_DLLS = ["CohrHOPS", "CohrFTCI2C"]
for dll_name in REQUIRED_DLLS:
    dll_path = find_library(dll_name)
    if dll_path is None:
        raise FileNotFoundError(f"Required 64-bit DLL file not found: {dll_name}.dll")

# Try to load the DLLs to ensure they're accessible
try:
    ctypes.CDLL(find_library("CohrHOPS"))
    ctypes.CDLL(find_library("CohrFTCI2C"))
except Exception as e:
    logger.error(f"Error loading 64-bit DLLs: {e}")
    raise

# from .device import HOPSDevice

# __all__ = ["HOPSDevice"]
