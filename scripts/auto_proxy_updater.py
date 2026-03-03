#!/usr/bin/env python3
"""
Automatic Proxy Updater
Fetches fresh proxies from multiple sources and validates them
"""

import schedule
import time
import requests
import subprocess
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.proxy_rotator import ProxyRotator

class AutoProxyUpdater:
    def __init__(self):
        self.logger = logging.getLogger('proxy_updater')
        self.setup_logging()
        
        self.proxy_sources = [
            {
                'name': 'Proxifly HTTPS',
                'url': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/https/data.txt',
                'file': 'proxies_proxifly.txt'
            },
            {
                'name': 'TheSpeedX HTTP',
                'url': 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt',
                'file': 'proxies_speedx.txt'
            },
            {
                'name': 'Proxifly SOCKS5',
                'url': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/socks5/data.txt',
                'file': 'proxies_socks5.txt'
            }
        ]
        
    def setup_logging(self):
        """Setup logging for updater"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/proxy_updater.log'),
                logging.StreamHandler()
            ]
        )
        
    def fetch_proxies(self):
        """Fetch proxies from all sources"""
        self.logger.info("🔄 Fetching fresh proxies...")
        
        all_proxies = []
        
        for source in self.proxy_sources:
            try:
                self.logger.info(f"📡 Fetching from {source['name']}")
                
                response = requests.get(
                    source['url'],
                    timeout=30,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                if response.status_code == 200:
                    proxies = response.text.strip().split('\n')
                    proxies = [p.strip() for p in proxies if p.strip()]
                    
                    # Save to individual file
                    with open(f'data/proxies/{source["file"]}', 'w') as f:
                        f.write('\n'.join(proxies))
                    
                    all_proxies.extend(proxies)
                    self.logger.info(f"✅ Got {len(proxies)} proxies from {source['name']}")
                else:
                    self.logger.warning(f"⚠️ Failed to fetch from {source['name']}: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"❌ Error fetching from {source['name']}: {e}")
        
        # Remove duplicates
        all_proxies = list(set(all_proxies))
        
        # Save combined list
        with open('config/proxies.txt', 'w') as f:
            f.write('# Auto-updated proxies\n')
            f.write(f'# Last updated: {datetime.now().isoformat()}\n')
            f.write('# Format: ip:port\n\n')
            for proxy in all_proxies:
                f.write(f"{proxy}\n")
        
        self.logger.info(f"📊 Total unique proxies: {len(all_proxies)}")
        return all_proxies
    
    def validate_proxies(self):
        """Validate fetched proxies"""
        self.logger.info("🔍 Validating proxies...")
        
        # Use ProxyRotator to validate
        rotator = ProxyRotator({
            'proxy_file': 'config/proxies.txt',
            'test_url': 'https://www.youtube.com',
            'max_failures': 3,
            'timeout': 10
        })
        
        rotator.load_proxies()
        working = rotator.validate_all(max_workers=100)
        
        self.logger.info(f"✅ Validation complete: {len(working)} working proxies")
        
        # Create timestamped backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        working_file = f'data/proxies/working_proxies_{timestamp}.txt'
        
        with open(working_file, 'w') as f:
            for proxy in working:
                f.write(f"{proxy}\n")
        
        # Symlink or copy to main working file
        import shutil
        shutil.copy2(working_file, 'data/proxies/working_proxies.txt')
        
        return working
    
    def update_cycle(self):
        """Complete update cycle"""
        self.logger.info("="*50)
        self.logger.info(f"Starting update cycle at {datetime.now()}")
        
        self.fetch_proxies()
        working = self.validate_proxies()
        
        self.logger.info(f"✅ Update cycle complete: {len(working)} working proxies")
        self.logger.info("="*50 + "\n")
    
    def run(self, interval_hours=1):
        """Run scheduler"""
        self.logger.info(f"🚀 Auto Proxy Updater Started (interval: {interval_hours} hours)")
        
        # Run immediately
        self.update_cycle()
        
        # Schedule hourly updates
        schedule.every(interval_hours).hours.do(self.update_cycle)
        
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    updater = AutoProxyUpdater()
    
    # Get interval from command line or use default
    interval = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    updater.run(interval)