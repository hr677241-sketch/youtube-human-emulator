#!/usr/bin/env python3
"""
View Scheduler - Schedule views throughout the day
"""

import schedule
import time
import random
import sys
from pathlib import Path
import logging
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import YouTubeHumanEmulator

class ViewScheduler:
    def __init__(self, config_path='config/settings.json'):
        self.emulator = YouTubeHumanEmulator(config_path)
        self.logger = logging.getLogger('scheduler')
        self.setup_logging()
        
        # Statistics
        self.views_today = 0
        self.target_views = 500
        self.last_reset = datetime.now().date()
        
    def setup_logging(self):
        """Setup logging for scheduler"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/scheduler.log'),
                logging.StreamHandler()
            ]
        )
    
    def reset_daily_counter(self):
        """Reset daily counter at midnight"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.views_today = 0
            self.last_reset = today
            self.logger.info("📅 Daily counter reset")
    
    def morning_session(self):
        """Morning viewing session (9 AM - 12 PM)"""
        self.reset_daily_counter()
        
        if self.views_today >= self.target_views:
            self.logger.info(f"🎯 Daily target reached: {self.views_today}/{self.target_views}")
            return
        
        self.logger.info("🌅 Starting morning session...")
        
        sessions = random.randint(5, 10)
        for i in range(sessions):
            if self.views_today >= self.target_views:
                break
                
            self.logger.info(f"📹 Morning session {i+1}/{sessions}")
            self.emulator.run_session()
            self.views_today += 1
            
            # Random delay between sessions
            delay = random.randint(180, 420)  # 3-7 minutes
            self.logger.info(f"⏳ Waiting {delay//60} minutes...")
            time.sleep(delay)
        
        self.logger.info(f"✅ Morning complete. Total today: {self.views_today}")
    
    def afternoon_session(self):
        """Afternoon viewing session (2 PM - 5 PM)"""
        self.reset_daily_counter()
        
        if self.views_today >= self.target_views:
            return
        
        self.logger.info("☀️ Starting afternoon session...")
        
        sessions = random.randint(8, 15)
        for i in range(sessions):
            if self.views_today >= self.target_views:
                break
                
            self.logger.info(f"📹 Afternoon session {i+1}/{sessions}")
            self.emulator.run_session()
            self.views_today += 1
            
            # Random delay
            delay = random.randint(120, 300)  # 2-5 minutes
            self.logger.info(f"⏳ Waiting {delay//60} minutes...")
            time.sleep(delay)
        
        self.logger.info(f"✅ Afternoon complete. Total today: {self.views_today}")
    
    def evening_session(self):
        """Evening viewing session (7 PM - 11 PM)"""
        self.reset_daily_counter()
        
        if self.views_today >= self.target_views:
            return
        
        self.logger.info("🌙 Starting evening session...")
        
        sessions = random.randint(10, 20)
        for i in range(sessions):
            if self.views_today >= self.target_views:
                break
                
            self.logger.info(f"📹 Evening session {i+1}/{sessions}")
            self.emulator.run_session()
            self.views_today += 1
            
            # Random delay
            delay = random.randint(180, 360)  # 3-6 minutes
            self.logger.info(f"⏳ Waiting {delay//60} minutes...")
            time.sleep(delay)
        
        self.logger.info(f"✅ Evening complete. Total today: {self.views_today}")
    
    def run_daily_schedule(self, target_views=500):
        """Run scheduled sessions"""
        self.target_views = target_views
        
        self.logger.info(f"📅 View Scheduler Started (Target: {target_views} views/day)")
        self.logger.info("⏰ Scheduled sessions:")
        self.logger.info("   - Morning: 9:00 AM - 12:00 PM")
        self.logger.info("   - Afternoon: 2:00 PM - 5:00 PM")
        self.logger.info("   - Evening: 7:00 PM - 11:00 PM")
        
        # Schedule sessions
        schedule.every().day.at("09:00").do(self.morning_session)
        schedule.every().day.at("14:00").do(self.afternoon_session)
        schedule.every().day.at("19:00").do(self.evening_session)
        
        # Check target every hour
        schedule.every().hour.do(self.check_progress)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("\n👋 Scheduler stopped")
            self.print_summary()
    
    def check_progress(self):
        """Check progress towards daily target"""
        self.reset_daily_counter()
        
        progress = (self.views_today / self.target_views) * 100
        self.logger.info(f"📊 Progress: {self.views_today}/{self.target_views} ({progress:.1f}%)")
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "="*60)
        print("📊 SCHEDULER SUMMARY")
        print("="*60)
        print(f"Total views today: {self.views_today}")
        print(f"Target: {self.target_views}")
        print(f"Progress: {(self.views_today/self.target_views)*100:.1f}%")
        print("="*60)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='YouTube View Scheduler')
    parser.add_argument('--target', type=int, default=500,
                       help='Daily view target (default: 500)')
    parser.add_argument('--config', type=str, default='config/settings.json',
                       help='Configuration file')
    
    args = parser.parse_args()
    
    scheduler = ViewScheduler(args.config)
    scheduler.run_daily_schedule(args.target)