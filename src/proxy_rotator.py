"""Proxy rotation and management module"""

import random
import requests
import time
import json
from pathlib import Path
from typing import List, Optional, Dict
import threading
import logging
from datetime import datetime

class ProxyRotator:
    """Manages proxy rotation and validation"""
    
    def __init__(self, config):
        self.config = config
        self.proxy_file = config.get('proxy_file', 'config/proxies.txt')
        self.test_url = config.get('test_url', 'https://www.youtube.com')
        self.max_failures = config.get('max_failures', 3)
        self.timeout = config.get('timeout', 10)
        
        self.proxies = []
        self.working_proxies = []
        self.failed_proxies = {}
        self.current_index = 0
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Stats
        self.stats = {
            'total_tested': 0,
            'working': 0,
            'failed': 0,
            'last_update': None
        }
    
    def load_proxies(self) -> List[str]:
        """Load proxies from file"""
        proxy_path = Path(self.proxy_file)
        
        if not proxy_path.exists():
            self.logger.warning(f"⚠️ Proxy file not found: {self.proxy_file}")
            return []
        
        with open(proxy_path, 'r') as f:
            self.proxies = [line.strip() for line in f if line.strip()]
        
        self.logger.info(f"📡 Loaded {len(self.proxies)} proxies from file")
        
        # Filter out comments
        self.proxies = [p for p in self.proxies if not p.startswith('#')]
                # Filter out comments
        self.proxies = [p for p in self.proxies if not p.startswith('#')]
        
        return self.proxies
    
    def test_proxy(self, proxy: str) -> bool:
        """Test if a proxy is working"""
        proxy_dict = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                self.test_url,
                proxies=proxy_dict,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            
            if response.status_code == 200:
                speed = time.time() - start_time
                self.logger.debug(f"✅ Proxy {proxy} working (speed: {speed:.2f}s)")
                return True
        except:
            pass
        
        return False
    
    def validate_all(self, max_workers: int = 50) -> List[str]:
        """Validate all proxies using multiple threads"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        self.logger.info(f"🔍 Validating {len(self.proxies)} proxies...")
        
        working = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in self.proxies
            }
            
            for future in as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        working.append(proxy)
                        self.stats['working'] += 1
                    else:
                        self.stats['failed'] += 1
                    
                    self.stats['total_tested'] += 1
                    
                    # Progress indicator
                    if self.stats['total_tested'] % 50 == 0:
                        self.logger.info(f"Progress: {self.stats['total_tested']}/{len(self.proxies)} "
                                       f"(Working: {self.stats['working']})")
                
                except Exception as e:
                    self.logger.debug(f"Error testing {proxy}: {e}")
        
        self.working_proxies = working
        self.stats['last_update'] = datetime.now().isoformat()
        
        # Save working proxies
        self._save_working_proxies()
        
        self.logger.info(f"✅ Validation complete: {len(working)} working proxies")
        return working
    
    def _save_working_proxies(self):
        """Save working proxies to file"""
        output_file = Path('data/proxies/working_proxies.txt')
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            for proxy in self.working_proxies:
                f.write(f"{proxy}\n")
        
        # Save stats
        stats_file = Path('data/proxies/proxy_stats.json')
        with open(stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_proxy(self) -> Optional[str]:
        """Get a random working proxy"""
        with self.lock:
            if not self.working_proxies:
                self.logger.warning("⚠️ No working proxies available")
                return None
            
            # Rotate through proxies
            proxy = random.choice(self.working_proxies)
            
            # Check if proxy has failed too many times
            if proxy in self.failed_proxies:
                if self.failed_proxies[proxy] >= self.max_failures:
                    self.working_proxies.remove(proxy)
                    self.logger.warning(f"❌ Removing {proxy} after {self.max_failures} failures")
                    return self.get_proxy()
            
            return proxy
    
    def report_failure(self, proxy: str):
        """Report a proxy failure"""
        with self.lock:
            self.failed_proxies[proxy] = self.failed_proxies.get(proxy, 0) + 1
            failures = self.failed_proxies[proxy]
            
            self.logger.debug(f"📊 Proxy {proxy} failures: {failures}/{self.max_failures}")
            
            if failures >= self.max_failures:
                if proxy in self.working_proxies:
                    self.working_proxies.remove(proxy)
                self.logger.warning(f"❌ Removed {proxy} after {failures} failures")
    
    def refresh_proxies(self):
        """Refresh proxy list from source"""
        self.logger.info("🔄 Refreshing proxy list...")
        
        # Reset stats
        self.failed_proxies = {}
        
        # Reload from file
        self.load_proxies()
        
        # Validate new proxies
        self.validate_all()
        
        self.logger.info(f"✅ Proxy refresh complete: {len(self.working_proxies)} working")