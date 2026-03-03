"""Browser manager with anti-detection features"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import random
import time
import logging

class AdvancedBrowserManager:
    """Manages browser instances with anti-detection"""
    
    def __init__(self, proxy=None, profile_dir=None, headless=False):
        self.proxy = proxy
        self.profile_dir = profile_dir
        self.headless = headless
        self.driver = None
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)
    
    def create_driver(self):
        """Create undetected Chrome driver"""
        options = uc.ChromeOptions()
        
        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        
        # Random user agent
        options.add_argument(f'--user-agent={self.ua.random}')
        
        # Window size
        options.add_argument('--window-size=1920,1080')
        
        # Headless mode
        if self.headless:
            options.add_argument('--headless=new')
        
        # Proxy
        if self.proxy:
            options.add_argument(f'--proxy-server=http://{self.proxy}')
        
        # Create driver
        self.driver = uc.Chrome(options=options)
        
        return self.driver
    
    def close(self):
        """Close browser"""
        if self.driver:
            self.driver.quit()
