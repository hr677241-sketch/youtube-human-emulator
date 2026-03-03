"""Human behavior simulation module"""

import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging

class HumanEmulator:
    """Simulates human-like behavior in browser"""
    
    def __init__(self, driver, config):
        self.driver = driver
        self.config = config
        self.actions = ActionChains(driver)
        self.logger = logging.getLogger(__name__)
        
        # Comments database
        self.comments = [
            "Great video! Really enjoyed it 👍",
            "Very informative, thanks for sharing",
            "This helped me understand the topic better",
            "Awesome content as always!",
            "First time watching, definitely subscribing",
            "Quality content right here",
            "Underrated channel, deserves more views",
            "Learned something new today, thanks!",
            "Keep up the great work!",
            "This deserves way more views",
            "Excellent explanation, very clear",
            "Subscribed! Looking forward to more",
            "One of the best videos on this topic",
            "Really helpful, thanks a lot",
            "Amazing quality, keep it up"
        ]
    
    def human_type(self, element, text):
        """Type text like a human with random delays"""
        for char in text:
            element.send_keys(char)
            
            # Random delay between keystrokes
            speed_config = self.config.get('human_like', {}).get('typing_speed', {})
            min_delay = speed_config.get('min', 0.08)
            max_delay = speed_config.get('max', 0.25)
            
            time.sleep(random.uniform(min_delay, max_delay))
            
            # Occasionally pause longer (like thinking)
            if random.random() < 0.05:
                time.sleep(random.uniform(1, 3))
    
    def watch_video_naturally(self, video_element, min_time, max_time):
        """Watch video with natural behavior"""
        watch_time = random.randint(min_time, max_time)
        start_time = time.time()
        
        self.logger.info(f"▶️ Watching video for ~{watch_time//60}m {watch_time%60}s")
        
        # Click to ensure focus/play
        try:
            video_element.click()
        except:
            pass
        
        time.sleep(random.uniform(1, 3))
        
        # Watch with occasional pauses/interactions
        while time.time() - start_time < watch_time:
            elapsed = time.time() - start_time
            
            # Random interactions during viewing
            if random.random() < 0.1:  # 10% chance per loop
                interaction = random.choice(['pause', 'scroll', 'mouse_move'])
                
                if interaction == 'pause':
                    self._simulate_pause_resume(video_element)
                elif interaction == 'scroll':
                    self._random_scroll_comments()
                elif interaction == 'mouse_move':
                    self._random_mouse_move()
            
            # Wait before next check
            time.sleep(random.uniform(5, 15))
        
        self.logger.info("✅ Finished watching video")
    
    def _simulate_pause_resume(self, video_element):
        """Simulate pausing and resuming video"""
        self.logger.debug("⏸️ Pausing video...")
        
        try:
            video_element.click()
            pause_time = random.uniform(2, 8)
            time.sleep(pause_time)
            
            self.logger.debug("▶️ Resuming video...")
            video_element.click()
        except:
            pass
    
    def _random_scroll_comments(self):
        """Scroll through comments section"""
        try:
            # Find comments section
            comments = self.driver.find_elements(By.CSS_SELECTOR, 
                'ytd-comment-thread-renderer, #comments')
            
            if comments:
                # Scroll to comments
                self.driver.execute_script(
                    "arguments[0].scrollIntoView();", 
                    comments[0]
                )
                
                time.sleep(random.uniform(1, 3))
                
                # Scroll through comments
                for _ in range(random.randint(1, 3)):
                    self.driver.execute_script("window.scrollBy(0, 200);")
                    time.sleep(random.uniform(0.5, 1.5))
        except:
            pass
    
    def _random_mouse_move(self):
        """Random mouse movement"""
        try:
            # Get viewport size
            width = self.driver.execute_script("return window.innerWidth")
            height = self.driver.execute_script("return window.innerHeight")
            
            # Random position
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)
            
            # Move mouse
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(self.driver)
            actions.move_by_offset(x, y)
            actions.perform()
            
            time.sleep(random.uniform(0.2, 0.5))
        except:
            pass
    
    def random_interaction(self):
        """Perform random interaction with the video"""
        interaction_type = random.choice(['like', 'comment', 'subscribe'])
        
        self.logger.info(f"🎯 Random interaction: {interaction_type}")
        
        if interaction_type == 'like':
            self._click_like()
        elif interaction_type == 'comment':
            self._post_comment()
        elif interaction_type == 'subscribe':
            self._click_subscribe()
    
    def _click_like(self):
        """Click like button"""
        try:
            # Try multiple selectors for like button
            selectors = [
                'button[aria-label*="like"]',
                'button[aria-label*="Like"]',
                '#top-level-buttons ytd-toggle-button-renderer:first-child',
                'ytd-segmented-like-dislike-button-renderer button:first-child'
            ]
            
            for selector in selectors:
                try:
                    like_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    like_button.click()
                    self.logger.info("👍 Liked video")
                    time.sleep(random.uniform(1, 3))
                    return
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Like button not found: {e}")
    
    def _post_comment(self):
        """Post a random comment"""
        try:
            # Find comment box
            selectors = [
                'div#placeholder-area',
                'div[contenteditable="true"]',
                '#simplebox-placeholder',
                'ytd-comment-simplebox-renderer #placeholder-area'
            ]
            
            comment_box = None
            for selector in selectors:
                try:
                    comment_box = self.driver.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
            
            if not comment_box:
                return
            
            # Click on comment box
            comment_box.click()
            time.sleep(random.uniform(1, 2))
            
            # Type comment
            comment = random.choice(self.comments)
            self.human_type(comment_box, comment)
            
            time.sleep(random.uniform(1, 3))
            
            # Find and click comment button
            comment_button_selectors = [
                'button[aria-label*="Comment"]',
                'ytd-button-renderer#button',
                '#submit-button'
            ]
            
            for selector in comment_button_selectors:
                try:
                    comment_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if comment_button.is_enabled():
                        comment_button.click()
                        self.logger.info(f"💬 Posted comment: '{comment[:30]}...'")
                        time.sleep(random.uniform(2, 5))
                        return
                except:
                    continue
                    
        except Exception as e:
            self.logger.debug(f"Comment posting failed: {e}")
    
    def _click_subscribe(self):
        """Click subscribe button"""
        try:
            selectors = [
                'button[aria-label*="Subscribe"]',
                'ytd-subscribe-button-renderer button',
                '#subscribe-button button'
            ]
            
            for selector in selectors:
                try:
                    sub_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    sub_button.click()
                    self.logger.info("🔔 Subscribed to channel")
                    time.sleep(random.uniform(2, 4))
                    return
                except:
                    continue
        except Exception as e:
            self.logger.debug(f"Subscribe button not found: {e}")