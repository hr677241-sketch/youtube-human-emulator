#!/usr/bin/env python3
"""
YouTube Human Emulator - Main Entry Point
Educational Purpose Only
"""

import argparse
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import setup_logging, load_config
from src.advanced_browser import AdvancedBrowserManager
from src.human_emulator import HumanEmulator
from src.proxy_rotator import ProxyRotator
import logging
import time
import random

class YouTubeHumanEmulator:
    """Main application class"""
    
    def __init__(self, config_path='config/settings.json'):
        self.config = load_config(config_path)
        self.logger = setup_logging(self.config.get('logging', {}))
        self.proxy_rotator = None
        self.stats = {'sessions': 0, 'views': 0, 'errors': 0}
        
    def initialize(self):
        """Initialize components"""
        self.logger.info("🚀 Initializing YouTube Human Emulator")
        
        # Initialize proxy rotator if enabled
        if self.config.get('proxy', {}).get('enabled', False):
            self.proxy_rotator = ProxyRotator(self.config['proxy'])
            self.proxy_rotator.load_proxies()
            
        self.logger.info("✅ Initialization complete")
        
    def run_session(self, url=None):
        """Run a single viewing session"""
        if not url:
            url = random.choice(self.config['youtube_urls'])
            
        # Get proxy for this session
        proxy = None
        if self.proxy_rotator:
            proxy = self.proxy_rotator.get_proxy()
            if proxy:
                self.logger.info(f"📡 Using proxy: {proxy}")
                
        try:
            # Create browser instance
            browser = AdvancedBrowserManager(
                proxy=proxy,
                profile_dir=f"sessions/profiles/session_{int(time.time())}"
            )
            
            driver = browser.create_driver()
            
            # Navigate to video
            browser.human_like_navigation(url)
            
            # Create human emulator
            human = HumanEmulator(driver, self.config)
            
            # Find and interact with video
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            video = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    'video, .video-stream, .html5-main-video'))
            )
            
            # Watch video with human behavior
            min_time = self.config['behavior']['min_watch_time']
            max_time = self.config['behavior']['max_watch_time']
            
            human.watch_video_naturally(video, min_time, max_time)
            
            # Random interactions
            if random.random() < self.config['behavior'].get('interaction_probability', 0.3):
                human.random_interaction()
                
            # Update stats
            self.stats['sessions'] += 1
            self.stats['views'] += 1
            
            self.logger.info(f"✅ Session complete. Total views: {self.stats['views']}")
            
            # Cleanup
            browser.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Session error: {e}")
            self.stats['errors'] += 1
            
            # Report proxy failure
            if proxy and self.proxy_rotator:
                self.proxy_rotator.report_failure(proxy)
                
            return False
            
    def run_continuous(self, interval_minutes=5):
        """Run continuous sessions"""
        self.logger.info(f"🔄 Starting continuous mode (interval: {interval_minutes} minutes)")
        
        try:
            while True:
                self.run_session()
                
                # Random delay between sessions
                delay = interval_minutes * 60 * random.uniform(0.8, 1.2)
                self.logger.info(f"⏳ Waiting {delay/60:.1f} minutes until next session")
                time.sleep(delay)
                
        except KeyboardInterrupt:
            self.logger.info("👋 Shutting down...")
            self.print_stats()
            
    def print_stats(self):
        """Print session statistics"""
        print("\n" + "="*50)
        print("📊 SESSION STATISTICS")
        print("="*50)
        print(f"Total sessions: {self.stats['sessions']}")
        print(f"Total views: {self.stats['views']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"Success rate: {(self.stats['sessions']/(self.stats['sessions']+self.stats['errors']+0.01))*100:.1f}%")
        print("="*50)

def main():
    parser = argparse.ArgumentParser(description='YouTube Human Emulator')
    parser.add_argument('--config', type=str, default='config/settings.json',
                       help='Path to configuration file')
    parser.add_argument('--url', type=str, help='Single YouTube URL to process')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run in continuous mode')
    parser.add_argument('--interval', type=int, default=5,
                       help='Interval between sessions in minutes (default: 5)')
    parser.add_argument('--sessions', type=int, help='Number of sessions to run')
    
    args = parser.parse_args()
    
    # Create and initialize emulator
    emulator = YouTubeHumanEmulator(args.config)
    emulator.initialize()
    
    # Run based on arguments
    if args.continuous:
        emulator.run_continuous(args.interval)
    elif args.sessions:
        for i in range(args.sessions):
            print(f"\n📹 Session {i+1}/{args.sessions}")
            emulator.run_session(args.url)
            if i < args.sessions - 1:
                time.sleep(random.randint(60, 180))
        emulator.print_stats()
    else:
        emulator.run_session(args.url)
        emulator.print_stats()

if __name__ == '__main__':
    main()