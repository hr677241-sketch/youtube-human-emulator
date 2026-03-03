"""Advanced browser manager with anti-detection features"""

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from fake_useragent import UserAgent
import random
import time
import json
import os
from pathlib import Path
import logging

class AdvancedBrowserManager:
    """Manages browser instances with advanced anti-detection"""
    
    def __init__(self, proxy=None, profile_dir=None, headless=False):
        self.proxy = proxy
        self.profile_dir = profile_dir
        self.headless = headless
        self.driver = None
        self.ua = UserAgent()
        self.logger = logging.getLogger(__name__)
        
        # Create profile directory if needed
        if profile_dir:
            Path(profile_dir).mkdir(parents=True, exist_ok=True)
    
    def generate_fingerprint(self):
        """Generate unique browser fingerprint"""
        
        # Screen resolutions (human-like)
        resolutions = [
            (1920, 1080), (1366, 768), (1536, 864),
            (1440, 900), (1280, 720), (2560, 1440)
        ]
        
        # Timezones
        timezones = [
            'America/New_York', 'Europe/London', 'Asia/Tokyo',
            'Australia/Sydney', 'America/Los_Angeles', 'Europe/Paris'
        ]
        
        # Languages
        languages = [
            'en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7',
            'en-AU,en;q=0.8', 'en-NZ,en;q=0.7'
        ]
        
        # Platforms
        platforms = ['Win32', 'MacIntel', 'Linux x86_64']
        
        # WebGL vendors
        webgl_vendors = [
            'Intel Inc.', 'NVIDIA Corporation', 'AMD',
            'Google Inc.', 'Apple Inc.'
        ]
        
        # Renderers
        renderers = [
            'Intel Iris OpenGL Engine',
            'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11)',
            'WebKit WebGL',
            'Mesa Offscreen'
        ]
        
        width, height = random.choice(resolutions)
        
        return {
            'user_agent': self.ua.random,
            'screen_width': width,
            'screen_height': height,
            'timezone': random.choice(timezones),
            'language': random.choice(languages),
            'platform': random.choice(platforms),
            'webgl_vendor': random.choice(webgl_vendors),
            'renderer': random.choice(renderers),
            'color_depth': random.choice([24, 30, 48]),
            'pixel_ratio': random.choice([1, 1.25, 1.5, 2]),
            'hardware_concurrency': random.choice([2, 4, 8, 16]),
            'device_memory': random.choice([2, 4, 8, 16])
        }
    
    def create_driver(self):
        """Create undetected Chrome driver with fingerprint"""
        fingerprint = self.generate_fingerprint()
        
        options = uc.ChromeOptions()
        
        # Anti-detection arguments
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        options.add_argument('--disable-dev-tools')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--no-pings')
        
        # Apply fingerprint
        options.add_argument(f'--user-agent={fingerprint["user_agent"]}')
        options.add_argument(f'--lang={fingerprint["language"]}')
        options.add_argument(f'--window-size={fingerprint["screen_width"]},{fingerprint["screen_height"]}')
        
        # Proxy configuration
        if self.proxy:
            options.add_argument(f'--proxy-server=http://{self.proxy}')
        
        # Profile directory
        if self.profile_dir:
            options.add_argument(f'--user-data-dir={self.profile_dir}')
        
        # Headless mode
        if self.headless:
            options.add_argument('--headless=new')
        
        # Additional stealth arguments
        options.add_argument('--disable-session-crashed-bubble')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--ignore-certificate-errors')
        
        try:
            # Create driver with random Chrome version
            self.driver = uc.Chrome(
                options=options,
                version_main=random.randint(114, 120),
                headless=self.headless
            )
            
            # Apply stealth scripts
            self._apply_stealth(fingerprint)
            
            # Set window position randomly
            self.driver.set_window_position(
                random.randint(0, 100),
                random.randint(0, 100)
            )
            
            self.logger.info(f"✅ Browser created with fingerprint: {fingerprint['platform']}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create driver: {e}")
            # Fallback to default Chrome
            self.driver = uc.Chrome(options=options)
        
        return self.driver
    
    def _apply_stealth(self, fingerprint):
        """Apply advanced stealth scripts"""
        
        # Main stealth script
        stealth_script = f"""
        // Override navigator properties
        Object.defineProperty(navigator, 'webdriver', {{
            get: () => undefined
        }});
        
        Object.defineProperty(navigator, 'plugins', {{
            get: () => [1, 2, 3, 4, 5]
        }});
        
        Object.defineProperty(navigator, 'languages', {{
            get: () => ['{fingerprint["language"].split(",")[0]}', 'en']
        }});
        
        Object.defineProperty(navigator, 'platform', {{
            get: () => '{fingerprint["platform"]}'
        }});
        
        Object.defineProperty(navigator, 'hardwareConcurrency', {{
            get: () => {fingerprint["hardware_concurrency"]}
        }});
        
        Object.defineProperty(navigator, 'deviceMemory', {{
            get: () => {fingerprint["device_memory"]}
        }});
        
        // Override WebGL fingerprint
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {{
            if (parameter === 37445) {{
                return '{fingerprint["webgl_vendor"]}';
            }}
            if (parameter === 37446) {{
                return '{fingerprint["renderer"]}';
            }}
            return getParameter(parameter);
        }};
        
        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({{ state: 'denied' }}) :
                originalQuery(parameters)
        );
        
        // Add chrome runtime
        window.chrome = {{
            runtime: {{}},
            app: {{}},
            csi: () => {{}},
            loadTimes: () => {{}}
        }};
        
        // Override connection
        Object.defineProperty(navigator, 'connection', {{
            get: () => ({{
                rtt: {random.randint(50, 200)},
                downlink: {random.randint(5, 50)},
                effectiveType: '{random.choice(["4g", "3g"])}',
                saveData: false
            }})
        }});
        
        // Override screen
        Object.defineProperty(screen, 'width', {{ value: {fingerprint["screen_width"]} }});
        Object.defineProperty(screen, 'height', {{ value: {fingerprint["screen_height"]} }});
        Object.defineProperty(screen, 'availWidth', {{ value: {fingerprint["screen_width"]} }});
        Object.defineProperty(screen, 'availHeight', {{ value: {fingerprint["screen_height"] - 40} }});
        Object.defineProperty(screen, 'colorDepth', {{ value: {fingerprint["color_depth"]} }});
        Object.defineProperty(screen, 'pixelDepth', {{ value: {fingerprint["color_depth"]} }});
        
        // Override devicePixelRatio
        Object.defineProperty(window, 'devicePixelRatio', {{
            get: () => {fingerprint["pixel_ratio"]}
        }});
        """
        
        try:
            self.driver.execute_script(stealth_script)
            self.logger.debug("✅ Stealth scripts applied")
        except Exception as e:
            self.logger.warning(f"⚠️ Stealth script error: {e}")
    
    def human_like_navigation(self, url):
        """Navigate with human-like behavior"""
        
        # Random pre-navigation delay
        time.sleep(random.uniform(1, 4))
        
        # Navigate
        self.logger.info(f"🌐 Navigating to: {url}")
        self.driver.get(url)
        
        # Random load time variation
        load_time = random.uniform(2, 6)
        time.sleep(load_time)
        
        # Simulate reading initial content
        time.sleep(random.uniform(1, 3))
    
    def random_mouse_movement(self):
        """Simulate random mouse movements"""
        actions = ActionChains(self.driver)
        
        # Get viewport size
        viewport_width = self.driver.execute_script("return window.innerWidth")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        # Random number of movements
        for _ in range(random.randint(3, 8)):
            x = random.randint(100, viewport_width - 100)
            y = random.randint(100, viewport_height - 100)
            
            # Move with bezier curve effect
            actions.move_by_offset(x, y)
            actions.perform()
            
            # Small random pause
            time.sleep(random.uniform(0.1, 0.4))
    
    def random_scroll(self):
        """Simulate natural scrolling"""
        scroll_height = self.driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        viewport_height = self.driver.execute_script("return window.innerHeight")
        
        # Don't scroll if page is short
        if scroll_height <= viewport_height + 100:
            return
        
        # Random scroll pattern
        pattern = random.choice(['smooth', 'jumpy', 'reading'])
        
        if pattern == 'smooth':
            # Smooth scrolling
            current = 0
            while current < scroll_height - viewport_height:
                step = random.randint(50, 150)
                current += step
                self.driver.execute_script(f"window.scrollTo(0, {current});")
                time.sleep(random.uniform(0.1, 0.3))
                
        elif pattern == 'jumpy':
            # Jump to random sections
            for _ in range(random.randint(2, 5)):
                jump_to = random.randint(0, scroll_height - viewport_height)
                self.driver.execute_script(f"window.scrollTo(0, {jump_to});")
                time.sleep(random.uniform(0.5, 2))
                
        elif pattern == 'reading':
            # Slow, methodical scrolling
            current = 0
            while current < scroll_height - viewport_height:
                step = random.randint(30, 80)
                current += step
                self.driver.execute_script(f"window.scrollTo(0, {current});")
                time.sleep(random.uniform(0.3, 0.8))
        
        # Sometimes scroll back up
        if random.random() < 0.3:
            time.sleep(random.uniform(1, 3))
            self.driver.execute_script(f"window.scrollTo(0, 0);")
    
    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("✅ Browser closed")
            except:
                pass
