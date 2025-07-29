#!/usr/bin/env python3
"""
Cookie refresh utility for Okta-authenticated OpenSearch sessions
"""
import os
import time
import json
import logging
from datetime import datetime, timedelta
from config import opensearch_config
from opensearch_service import OpenSearchService

logger = logging.getLogger(__name__)

class CookieManager:
    def __init__(self, config_path=".env"):
        self.config_path = config_path
        self.last_refresh = None
        self.refresh_interval = timedelta(hours=8)  # Refresh every 8 hours
        
    def is_cookie_valid(self):
        """Test if current cookies are still valid"""
        try:
            service = OpenSearchService(opensearch_config)
            health = service.get_cluster_health()
            logger.info(f"Cookie validation successful: {health.cluster_name}")
            return True
        except Exception as e:
            logger.warning(f"Cookie validation failed: {e}")
            return False
    
    def needs_refresh(self):
        """Check if cookies need refresh based on time or validity"""
        if not self.last_refresh:
            return True
        
        # Check time-based refresh
        if datetime.now() - self.last_refresh > self.refresh_interval:
            logger.info("Cookies expired based on time interval")
            return True
        
        # Check validity-based refresh
        if not self.is_cookie_valid():
            logger.info("Cookies invalid based on API test")
            return True
        
        return False
    
    def refresh_cookies_interactive(self):
        """Interactive cookie refresh process"""
        print("🔄 Cookie refresh required")
        print("Please follow these steps:")
        print("1. Open your browser")
        print("2. Go to OpenSearch Dashboards")
        print("3. Login through Okta if needed")
        print("4. Open Developer Tools (F12) → Network tab")
        print("5. Make any search or API call")
        print("6. Right-click on request → Copy → Copy as cURL")
        print("7. Paste the cURL command below")
        
        curl_command = input("\nPaste cURL command: ").strip()
        
        # Extract cookies from cURL command
        if 'Cookie:' in curl_command:
            cookie_part = curl_command.split("Cookie: ")[1].split("'")[0]
            return self.update_env_cookies(cookie_part)
        else:
            print("❌ No Cookie header found in cURL command")
            return False
    
    def update_env_cookies(self, cookie_string):
        """Update .env file with new cookies"""
        try:
            # Read existing .env
            env_vars = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            env_vars[key] = value.strip('"')
            
            # Update cookies
            env_vars['OPENSEARCH_USE_COOKIES'] = 'true'
            env_vars['OPENSEARCH_COOKIES'] = cookie_string
            
            # Write back
            with open(self.config_path, 'w') as f:
                f.write(f"# Updated: {datetime.now().isoformat()}\n")
                for key, value in env_vars.items():
                    if 'COOKIES' in key:
                        f.write(f'{key}="{value}"\n')
                    else:
                        f.write(f'{key}={value}\n')
            
            self.last_refresh = datetime.now()
            print("✅ Cookies updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update cookies: {e}")
            return False
    
    def monitor_and_refresh(self, check_interval_minutes=60):
        """Continuously monitor and refresh cookies as needed"""
        print(f"🔄 Starting cookie monitor (checking every {check_interval_minutes} minutes)")
        
        while True:
            try:
                if self.needs_refresh():
                    print("🔄 Refreshing cookies...")
                    if self.refresh_cookies_interactive():
                        print("✅ Cookie refresh successful")
                    else:
                        print("❌ Cookie refresh failed")
                else:
                    print("✅ Cookies still valid")
                
                # Wait before next check
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n👋 Cookie monitor stopped")
                break
            except Exception as e:
                logger.error(f"Monitor error: {e}")
                time.sleep(60)  # Wait 1 minute on error

def main():
    print("🍪 Okta Cookie Management Utility")
    print("=" * 40)
    
    manager = CookieManager()
    
    print("Options:")
    print("1. Check current cookie validity")
    print("2. Refresh cookies now")
    print("3. Start continuous monitoring")
    
    choice = input("Choose option (1/2/3): ").strip()
    
    if choice == "1":
        if manager.is_cookie_valid():
            print("✅ Current cookies are valid")
        else:
            print("❌ Current cookies are invalid or expired")
            
    elif choice == "2":
        if manager.refresh_cookies_interactive():
            print("✅ Cookie refresh completed")
        else:
            print("❌ Cookie refresh failed")
            
    elif choice == "3":
        interval = input("Check interval in minutes (default 60): ").strip()
        interval = int(interval) if interval.isdigit() else 60
        manager.monitor_and_refresh(interval)
    
    else:
        print("Invalid option")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()