#!/usr/bin/env python3
"""
View Monitor - Track YouTube view counts over time
"""

import requests
import time
import json
from datetime import datetime
import matplotlib.pyplot as plt
import argparse
import sys
from pathlib import Path

class ViewMonitor:
    def __init__(self, video_id):
        self.video_id = video_id
        self.video_url = f"https://www.youtube.com/watch?v={video_id}"
        self.view_history = []
        self.data_file = f"data/view_data_{video_id}.json"
        
        # Load existing data if available
        self.load_data()
        
    def get_current_views(self):
        """Fetch current view count using multiple methods"""
        
        # Method 1: Try oEmbed API (most reliable)
        try:
            oembed_url = f"https://www.youtube.com/oembed?url={self.video_url}&format=json"
            response = requests.get(oembed_url, timeout=10)
            # oEmbed doesn't give view count directly but can confirm video exists
            if response.status_code == 200:
                # Try alternative API
                return self._get_views_from_api()
        except:
            pass
        
        # Method 2: Try web scraping
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.video_url, headers=headers, timeout=10)
            
            # Look for view count in HTML
            import re
            patterns = [
                r'"viewCount":"(\d+)"',
                r'"viewCount":(\d+)',
                r'<span class="view-count">([^<]+)</span>',
                r'<meta itemprop="interactionCount" content="([^"]+)"'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, response.text)
                if match:
                    view_text = match.group(1)
                    # Clean up text (remove commas, "views", etc.)
                    view_text = re.sub(r'[^0-9]', '', view_text)
                    if view_text:
                        return int(view_text)
        except:
            pass
        
        return None
    
    def _get_views_from_api(self):
        """Try to get views from YouTube API (requires API key)"""
        # This would require a YouTube Data API key
        # For demo purposes, return None
        return None
    
    def monitor(self, duration_hours=24, interval_minutes=5):
        """Monitor view count over time"""
        print(f"🎬 Monitoring views for video: {self.video_url}")
        print(f"⏱️  Duration: {duration_hours} hours")
        print(f"⏰ Interval: {interval_minutes} minutes")
        print("-" * 60)
        
        start_time = datetime.now()
        end_time = start_time.timestamp() + (duration_hours * 3600)
        
        # Get initial view count
        initial_views = self.get_current_views()
        if initial_views is None:
            print("❌ Could not fetch initial view count")
            return
        
        print(f"📊 Initial views: {initial_views:,}")
        
        while time.time() < end_time:
            try:
                current_views = self.get_current_views()
                
                if current_views is not None:
                    data_point = {
                        'timestamp': datetime.now().isoformat(),
                        'views': current_views,
                        'increase': current_views - initial_views
                    }
                    
                    self.view_history.append(data_point)
                    self.save_data()
                    
                    print(f"[{data_point['timestamp']}] Views: {current_views:,} "
                          f"(+{data_point['increase']:,})")
                else:
                    print(f"[{datetime.now().isoformat()}] ⚠️ Could not fetch views")
                
                # Wait for next interval
                time.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n👋 Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                time.sleep(60)
        
        # Show summary
        self.print_summary()
        self.plot_results()
    
    def print_summary(self):
        """Print monitoring summary"""
        if not self.view_history:
            return
        
        first = self.view_history[0]
        last = self.view_history[-1]
        total_increase = last['views'] - first['views']
        
        print("\n" + "="*60)
        print("📊 MONITORING SUMMARY")
        print("="*60)
        print(f"Video ID: {self.video_id}")
        print(f"Start time: {first['timestamp']}")
        print(f"End time: {last['timestamp']}")
        print(f"Start views: {first['views']:,}")
        print(f"End views: {last['views']:,}")
        print(f"Total increase: {total_increase:,}")
        
        if total_increase > 0:
            duration_hours = len(self.view_history) * 5 / 60  # assuming 5-min intervals
            rate_per_hour = total_increase / duration_hours
            print(f"Average rate: {rate_per_hour:.1f} views/hour")
        
        print("="*60)
    
    def plot_results(self):
        """Plot view count over time"""
        if not self.view_history:
            return
        
        timestamps = [d['timestamp'] for d in self.view_history]
        views = [d['views'] for d in self.view_history]
        increases = [d['increase'] for d in self.view_history]
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot view count
        ax1.plot(range(len(views)), views, 'b-', linewidth=2)
        ax1.set_title('YouTube View Count Over Time')
        ax1.set_xlabel('Measurement')
        ax1.set_ylabel('View Count')
        ax1.grid(True, alpha=0.3)
        
        # Format y-axis with commas
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format(int(x), ',')))
        
        # Plot view increase
        ax2.plot(range(len(increases)), increases, 'g-', linewidth=2)
        ax2.set_title('View Increase')
        ax2.set_xlabel('Measurement')
        ax2.set_ylabel('Increase')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_file = f"data/view_plot_{self.video_id}.png"
        plt.savefig(plot_file, dpi=150)
        print(f"📈 Plot saved to: {plot_file}")
        
        plt.show()
    
    def load_data(self):
        """Load existing monitoring data"""
        data_path = Path(self.data_file)
        if data_path.exists():
            try:
                with open(data_path, 'r') as f:
                    data = json.load(f)
                    self.view_history = data.get('history', [])
                    print(f"📂 Loaded {len(self.view_history)} data points from {self.data_file}")
            except:
                pass
    
    def save_data(self):
        """Save monitoring data"""
        data_path = Path(self.data_file)
        data_path.parent.mkdir(exist_ok=True)
        
        data = {
            'video_id': self.video_id,
            'history': self.view_history,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(data_path, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Monitor YouTube View Count')
    parser.add_argument('video_id', help='YouTube Video ID')
    parser.add_argument('--duration', '-d', type=int, default=24,
                       help='Monitoring duration in hours (default: 24)')
    parser.add_argument('--interval', '-i', type=int, default=5,
                       help='Check interval in minutes (default: 5)')
    
    args = parser.parse_args()
    
    monitor = ViewMonitor(args.video_id)
    monitor.monitor(duration_hours=args.duration, interval_minutes=args.interval)

if __name__ == '__main__':
    main()