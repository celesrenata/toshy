"""
Toshy - Mac-style keybindings for Linux

A comprehensive keybinding solution that brings Mac-style keyboard shortcuts
to Linux desktop environments, supporting both X11 and Wayland.
"""

__version__ = "24.12.1"
__author__ = "RedBearAK"
__maintainer__ = "Celes Renata"
__email__ = "celes@celesrenata.com"
__license__ = "GPL-3.0-or-later"

from . import common
from . import gui

__all__ = ["common", "gui", "__version__"]
