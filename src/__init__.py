"""YouTube Human Emulator - Advanced YouTube automation with human-like behavior"""

__version__ = '2.0.0'
__author__ = 'Haroon Rasheed'
__license__ = 'MIT'

from .browser_manager import AdvancedBrowserManager as BrowserManager
from .human_emulator import HumanEmulator
from .proxy_rotator import ProxyRotator
from .tor_manager import TorManager
from .session_manager import SessionManager
from .advanced_browser import AdvancedBrowserManager
from .utils import setup_logging, load_config, validate_config