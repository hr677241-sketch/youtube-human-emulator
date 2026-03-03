"""Session management for browser profiles and cookies"""

import os
import json
import pickle
import time
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import hashlib

class SessionManager:
    """Manages browser sessions, profiles, and cookies"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize session manager
        
        Args:
            config: Session configuration dictionary
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Setup directories
        self.base_dir = Path('sessions')
        self.cookies_dir = self.base_dir / 'cookies'
        self.profiles_dir = self.base_dir / 'profiles'
        
        # Create directories if they don't exist
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Session tracking
        self.active_sessions = {}
        self.session_history = []
        self.max_concurrent = config.get('max_concurrent', 3)
        
        # Load existing sessions
        self._load_session_history()
    
    def create_session(self, video_url: str, proxy: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new session
        
        Args:
            video_url: YouTube video URL
            proxy: Optional proxy for this session
            
        Returns:
            dict: Session information
        """
        # Check concurrent session limit
        if len(self.active_sessions) >= self.max_concurrent:
            self.logger.warning(f"⚠️ Max concurrent sessions reached ({self.max_concurrent})")
            return None
        
        # Generate session ID
        session_id = self._generate_session_id()
        timestamp = datetime.now()
        
        # Create session profile
        profile_dir = self.profiles_dir / f"profile_{session_id}"
        profile_dir.mkdir(exist_ok=True)
        
        session = {
            'id': session_id,
            'video_url': video_url,
            'proxy': proxy,
            'profile_dir': str(profile_dir),
            'start_time': timestamp.isoformat(),
            'last_activity': timestamp.isoformat(),
            'status': 'active',
            'views_generated': 0,
            'watch_time': 0,
            'interactions': []
        }
        
        self.active_sessions[session_id] = session
        self.logger.info(f"✅ Created session: {session_id}")
        
        return session
    
    def end_session(self, session_id: str, success: bool = True) -> Dict[str, Any]:
        """
        End a session and archive it
        
        Args:
            session_id: Session ID to end
            success: Whether session completed successfully
            
        Returns:
            dict: Archived session data
        """
        if session_id not in self.active_sessions:
            self.logger.warning(f"⚠️ Session not found: {session_id}")
            return None
        
        session = self.active_sessions.pop(session_id)
        session['end_time'] = datetime.now().isoformat()
        session['status'] = 'completed' if success else 'failed'
        session['duration'] = self._calculate_duration(
            session['start_time'], 
            session['end_time']
        )
        
        # Save cookies if any
        self._save_session_cookies(session)
        
        # Add to history
        self.session_history.append(session)
        self._save_session_history()
        
        self.logger.info(f"✅ Ended session: {session_id} ({session['status']})")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get active session by ID"""
        return self.active_sessions.get(session_id)
    
    def update_session_activity(self, session_id: str, **kwargs):
        """Update session activity"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.update(kwargs)
            session['last_activity'] = datetime.now().isoformat()
    
    def add_interaction(self, session_id: str, interaction_type: str, details: Dict = None):
        """Record user interaction"""
        if session_id in self.active_sessions:
            interaction = {
                'type': interaction_type,
                'timestamp': datetime.now().isoformat(),
                'details': details or {}
            }
            self.active_sessions[session_id]['interactions'].append(interaction)
    
    def increment_views(self, session_id: str, count: int = 1):
        """Increment view count for session"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['views_generated'] += count
    
    def save_cookies(self, session_id: str, driver):
        """
        Save cookies from browser driver
        
        Args:
            session_id: Session ID
            driver: Selenium WebDriver instance
        """
        try:
            cookies = driver.get_cookies()
            if cookies:
                cookie_file = self.cookies_dir / f"cookies_{session_id}.pkl"
                with open(cookie_file, 'wb') as f:
                    pickle.dump(cookies, f)
                self.logger.debug(f"💾 Saved {len(cookies)} cookies for {session_id}")
        except Exception as e:
            self.logger.debug(f"Failed to save cookies: {e}")
    
    def load_cookies(self, session_id: str, driver) -> bool:
        """
        Load cookies for a session
        
        Args:
            session_id: Session ID
            driver: Selenium WebDriver instance
            
        Returns:
            bool: True if cookies loaded
        """
        cookie_file = self.cookies_dir / f"cookies_{session_id}.pkl"
        if not cookie_file.exists():
            return False
        
        try:
            with open(cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    pass
            
            self.logger.debug(f"📂 Loaded {len(cookies)} cookies for {session_id}")
            return True
        except Exception as e:
            self.logger.debug(f"Failed to load cookies: {e}")
            return False
    
    def cleanup_old_sessions(self, days: int = 7):
        """
        Remove old session data
        
        Args:
            days: Delete sessions older than this many days
        """
        cutoff = datetime.now() - timedelta(days=days)
        count = 0
        
        # Clean old profiles
        for profile_dir in self.profiles_dir.glob("profile_*"):
            try:
                # Check directory creation time
                created = datetime.fromtimestamp(profile_dir.stat().st_ctime)
                if created < cutoff:
                    import shutil
                    shutil.rmtree(profile_dir)
                    count += 1
            except:
                pass
        
        # Clean old cookies
        for cookie_file in self.cookies_dir.glob("cookies_*.pkl"):
            try:
                created = datetime.fromtimestamp(cookie_file.stat().st_ctime)
                if created < cutoff:
                    cookie_file.unlink()
                    count += 1
            except:
                pass
        
        if count > 0:
            self.logger.info(f"🧹 Cleaned up {count} old session files")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            dict: Session statistics
        """
        total_sessions = len(self.session_history)
        completed = sum(1 for s in self.session_history if s['status'] == 'completed')
        failed = sum(1 for s in self.session_history if s['status'] == 'failed')
        
        total_views = sum(s.get('views_generated', 0) for s in self.session_history)
        total_watch_time = sum(s.get('watch_time', 0) for s in self.session_history)
        
        return {
            'active_sessions': len(self.active_sessions),
            'total_sessions': total_sessions,
            'completed_sessions': completed,
            'failed_sessions': failed,
            'success_rate': (completed / total_sessions * 100) if total_sessions > 0 else 0,
            'total_views': total_views,
            'total_watch_time_hours': round(total_watch_time / 3600, 2),
            'avg_views_per_session': round(total_views / total_sessions, 2) if total_sessions > 0 else 0
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_num = random.randint(1000, 9999)
        return f"{timestamp}_{random_num}"
    
    def _calculate_duration(self, start: str, end: str) -> int:
        """Calculate session duration in seconds"""
        start_time = datetime.fromisoformat(start)
        end_time = datetime.fromisoformat(end)
        return int((end_time - start_time).total_seconds())
    
    def _save_session_cookies(self, session: Dict[str, Any]):
        """Save session data to cookies file"""
        cookie_file = self.cookies_dir / f"session_{session['id']}.json"
        try:
            with open(cookie_file, 'w') as f:
                json.dump(session, f, indent=2, default=str)
        except:
            pass
    
    def _save_session_history(self):
        """Save session history to file"""
        history_file = self.base_dir / 'session_history.json'
        try:
            with open(history_file, 'w') as f:
                json.dump(self.session_history[-100:], f, indent=2, default=str)
        except:
            pass
    
    def _load_session_history(self):
        """Load session history from file"""
        history_file = self.base_dir / 'session_history.json'
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    self.session_history = json.load(f)
                self.logger.info(f"📂 Loaded {len(self.session_history)} past sessions")
            except:
                self.session_history = []
    
    def rotate_user_agent(self, session_id: str) -> Optional[str]:
        """
        Rotate user agent for a session
        
        Args:
            session_id: Session ID
            
        Returns:
            str: New user agent
        """
        from fake_useragent import UserAgent
        ua = UserAgent()
        new_ua = ua.random
        
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['user_agent'] = new_ua
        
        return new_ua
    
    def get_session_fingerprint(self, session_id: str) -> Dict[str, Any]:
        """
        Get browser fingerprint for session
        
        Args:
            session_id: Session ID
            
        Returns:
            dict: Browser fingerprint
        """
        session = self.get_session(session_id)
        if not session:
            return {}
        
        # Generate consistent fingerprint based on session ID
        hash_obj = hashlib.md5(session_id.encode())
        hash_hex = hash_obj.hexdigest()
        
        return {
            'session_id': session_id,
            'screen_resolution': self._get_resolution_from_hash(hash_hex),
            'timezone': self._get_timezone_from_hash(hash_hex),
            'language': self._get_language_from_hash(hash_hex),
            'platform': self._get_platform_from_hash(hash_hex),
            'user_agent': session.get('user_agent', 'unknown')
        }
    
    def _get_resolution_from_hash(self, hash_hex: str) -> str:
        """Generate resolution from hash"""
        resolutions = [
            '1920,1080', '1366,768', '1536,864',
            '1440,900', '1280,720', '2560,1440'
        ]
        index = int(hash_hex[:2], 16) % len(resolutions)
        return resolutions[index]
    
    def _get_timezone_from_hash(self, hash_hex: str) -> str:
        """Generate timezone from hash"""
        timezones = [
            'America/New_York', 'Europe/London', 'Asia/Tokyo',
            'Australia/Sydney', 'America/Los_Angeles', 'Europe/Paris'
        ]
        index = int(hash_hex[2:4], 16) % len(timezones)
        return timezones[index]
    
    def _get_language_from_hash(self, hash_hex: str) -> str:
        """Generate language from hash"""
        languages = [
            'en-US,en;q=0.9', 'en-GB,en;q=0.8', 'en-CA,en;q=0.7',
            'en-AU,en;q=0.8', 'en-NZ,en;q=0.7'
        ]
        index = int(hash_hex[4:6], 16) % len(languages)
        return languages[index]
    
    def _get_platform_from_hash(self, hash_hex: str) -> str:
        """Generate platform from hash"""
        platforms = ['Win32', 'MacIntel', 'Linux x86_64']
        index = int(hash_hex[6:8], 16) % len(platforms)
        return platforms[index]


# Simple test if run directly
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'max_concurrent': 3
    }
    
    manager = SessionManager(config)
    
    # Create test session
    session = manager.create_session(
        video_url='https://youtube.com/watch?v=test',
        proxy='192.168.1.1:8080'
    )
    
    if session:
        print(f"✅ Created session: {session['id']}")
        
        # Update activity
        manager.update_session_activity(session['id'], watch_time=120)
        manager.increment_views(session['id'], 5)
        manager.add_interaction(session['id'], 'like')
        
        # End session
        ended = manager.end_session(session['id'])
        print(f"✅ Ended session: {ended['status']}")
        
        # Get stats
        stats = manager.get_stats()
        print(f"\n📊 Session Stats:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Cleanup
        manager.cleanup_old_sessions(days=1)
