"""Tor integration for IP rotation and anonymity"""

import time
import random
import requests
import logging
from stem import Signal
from stem.control import Controller
import stem
import stem.socket

try:
    conn = stem.socket.ControlPort(port=9051)
except stem.SocketError as e:   # ✅ correct usage
    print(f"Tor connection failed: {e}")
from typing import Optional, Dict, Any

class TorManager:
    """Manages Tor connection for IP rotation"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Tor manager
        
        Args:
            config: Tor configuration dictionary
        """
        self.config = config
        self.controller = None
        self.session = None
        self.current_ip = None
        self.logger = logging.getLogger(__name__)
        self.renew_count = 0
        self.max_attempts = config.get('max_renew_attempts', 5)
        self.control_port = config.get('control_port', 9051)
        self.socks_port = config.get('socks_port', 9050)
        self.password = config.get('password', '')
        
    def connect(self) -> bool:
        """
        Establish connection to Tor
        
        Returns:
            bool: True if connected successfully
        """
        try:
            self.controller = Controller.from_port(port=self.control_port)
            
            # Authenticate
            if self.password:
                self.controller.authenticate(password=self.password)
            else:
                self.controller.authenticate()
            
            # Test connection
            self.current_ip = self._get_current_ip()
            self.logger.info(f"✅ Connected to Tor. Current IP: {self.current_ip}")
            
            # Setup SOCKS session
            self.session = requests.Session()
            self.session.proxies = {
                'http': f'socks5h://127.0.0.1:{self.socks_port}',
                'https': f'socks5h://127.0.0.1:{self.socks_port}'
            }
            
            return True
            
        except SocketError as e:
            self.logger.error(f"❌ Failed to connect to Tor: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Tor connection error: {e}")
            return False
    
    def renew_identity(self) -> bool:
        """
        Request a new Tor identity (new IP)
        
        Returns:
            bool: True if IP changed successfully
        """
        if not self.controller:
            self.logger.error("❌ Tor controller not connected")
            return False
        
        try:
            self.renew_count += 1
            
            if self.renew_count > self.max_attempts:
                wait_time = random.randint(60, 180)
                self.logger.warning(f"⚠️ Max renewal attempts. Waiting {wait_time}s...")
                time.sleep(wait_time)
                self.renew_count = 0
            
            self.logger.info("🔄 Renewing Tor identity...")
            
            # Send NEWNYM signal
            self.controller.signal(Signal.NEWNYM)
            
            # Wait for new identity
            time.sleep(self.controller.get_newnym_wait())
            
            # Verify IP changed
            new_ip = self._get_current_ip()
            if new_ip and new_ip != self.current_ip:
                self.logger.info(f"✅ IP changed: {self.current_ip} → {new_ip}")
                self.current_ip = new_ip
                return True
            else:
                self.logger.warning("⚠️ IP did not change, retrying...")
                return self.renew_identity()
                
        except Exception as e:
            self.logger.error(f"❌ Failed to renew Tor identity: {e}")
            return False
    
    def _get_current_ip(self) -> Optional[str]:
        """
        Get current Tor exit node IP
        
        Returns:
            str: Current IP address or None
        """
        try:
            if self.session:
                response = self.session.get('https://httpbin.org/ip', timeout=10)
                return response.json().get('origin')
            else:
                # Direct proxy request
                proxies = {
                    'http': f'socks5h://127.0.0.1:{self.socks_port}',
                    'https': f'socks5h://127.0.0.1:{self.socks_port}'
                }
                response = requests.get(
                    'https://httpbin.org/ip', 
                    proxies=proxies, 
                    timeout=10
                )
                return response.json().get('origin')
        except Exception as e:
            self.logger.debug(f"Failed to get IP: {e}")
            return None
    
    def get_proxy_dict(self) -> Dict[str, str]:
        """
        Get proxy dictionary for Selenium
        
        Returns:
            dict: Proxy configuration
        """
        return {
            'proxy': {
                'http': f'socks5://127.0.0.1:{self.socks_port}',
                'https': f'socks5://127.0.0.1:{self.socks_port}',
                'no_proxy': 'localhost,127.0.0.1'
            }
        }
    
    def get_requests_proxies(self) -> Dict[str, str]:
        """
        Get proxy dict for requests library
        
        Returns:
            dict: Proxies for requests
        """
        return {
            'http': f'socks5://127.0.0.1:{self.socks_port}',
            'https': f'socks5://127.0.0.1:{self.socks_port}'
        }
    
    def check_tor_running(self) -> bool:
        """
        Check if Tor is running
        
        Returns:
            bool: True if Tor is accessible
        """
        try:
            # Try to connect to control port
            with Controller.from_port(port=self.control_port) as controller:
                return True
        except:
            return False
    
    def get_tor_info(self) -> Dict[str, Any]:
        """
        Get Tor connection information
        
        Returns:
            dict: Tor status information
        """
        if not self.controller:
            return {'status': 'disconnected'}
        
        try:
            return {
                'status': 'connected',
                'ip': self.current_ip,
                'version': self.controller.get_version().version_str,
                'uptime': self.controller.get_uptime(),
                'circuits': len(self.controller.get_circuits()),
                'renew_count': self.renew_count
            }
        except:
            return {'status': 'error'}
    
    def close(self):
        """Close Tor connection"""
        if self.controller:
            try:
                self.controller.close()
                self.logger.info("✅ Tor connection closed")
            except:
                pass
        
        if self.session:
            self.session.close()


# Simple test if run directly
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    config = {
        'control_port': 9051,
        'socks_port': 9050,
        'max_renew_attempts': 3
    }
    
    tor = TorManager(config)
    
    if tor.connect():
        print(f"✅ Connected to Tor. IP: {tor.current_ip}")
        print(f"🔍 Tor info: {tor.get_tor_info()}")
        
        # Test renew
        if input("Renew IP? (y/n): ").lower() == 'y':
            tor.renew_identity()
        
        tor.close()
    else:
        print("❌ Failed to connect to Tor")
        print("Make sure Tor is running:")
        print("  - Linux/macOS: sudo systemctl start tor")
        print("  - Windows: Start Tor Browser")



