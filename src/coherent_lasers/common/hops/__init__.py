"""
HOPS DLL Utilities Package

This package contains utilities and drivers for coherent lasers that use CohrHOPS DLL files.

Setup:
1. Download the required DLL files from the release assets on GitHub.
2. Place the DLL files in this package alongside the respective .h files.
"""

import platform
import sys

# Ensure is windows
if not (sys.platform.startswith("win") and platform.machine().endswith("64")):
    raise OSError("This package only supports 64-bit Windows systems.")

from .main import HOPSDevice

__all__ = ["HOPSDevice"]
