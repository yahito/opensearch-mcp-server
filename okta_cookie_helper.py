#!/usr/bin/env python3
"""
Helper script to extract Okta session cookies for OpenSearch authentication
"""
import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def extract_okta_cookies(opensearch_url, okta_username=None, okta_password=None, headless=True):
    """
    Extract session cookies after Okta authentication
    
    Args:
        opensearch_url: URL to OpenSearch Dashboards
        okta_username: Okta username (optional, for automation)
        okta_password: Okta password (optional, for automation)
        headless: Run browser in headless mode
    
    Returns:
        Dictionary of cookies
    """
    print(f"🔐 Extracting Okta cookies from {opensearch_url}")
    
    # Setup Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(opensearch_url)
        
        if okta_username and okta_password:
            print("🤖 Attempting automatic login...")
            
            # Wait for Okta login page
            username_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "okta-signin-username"))
            )
            password_field = driver.find_element(By.ID, "okta-signin-password")
            submit_button = driver.find_element(By.ID, "okta-signin-submit")
            
            # Enter credentials
            username_field.send_keys(okta_username)
            password_field.send_keys(okta_password)
            submit_button.click()
            
            # Handle MFA if present (manual intervention required)
            print("⏳ Waiting for MFA completion (if required)...")
            
            # Wait for redirect to OpenSearch Dashboards
            WebDriverWait(driver, 60).until(
                lambda d: opensearch_url.split('/')[2] in d.current_url
            )
        else:
            print("👤 Please complete Okta login manually in the browser...")
            print("   Press Enter after successful login and redirect to OpenSearch Dashboards")
            input()
        
        # Wait a bit for all cookies to be set
        time.sleep(3)
        
        # Extract cookies
        cookies = driver.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
        
        print("✅ Successfully extracted cookies:")
        for name, value in cookie_dict.items():
            print(f"   {name}: {value[:20]}...")
        
        return cookie_dict
        
    except Exception as e:
        print(f"❌ Error extracting cookies: {e}")
        return {}
    finally:
        if driver:
            driver.quit()

def format_cookies_for_env(cookies):
    """Format cookies for environment variable"""
    cookie_pairs = [f"{name}={value}" for name, value in cookies.items()]
    return "; ".join(cookie_pairs)

def save_cookies_to_file(cookies, filename="opensearch_cookies.txt"):
    """Save cookies to file"""
    with open(filename, 'w') as f:
        for name, value in cookies.items():
            f.write(f"{name}={value}\n")
    print(f"💾 Cookies saved to {filename}")

def update_env_file(cookie_string):
    """Update .env file with extracted cookies"""
    env_path = ".env"
    
    # Read existing .env file
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    
    # Update cookie-related variables
    env_vars['OPENSEARCH_USE_COOKIES'] = 'true'
    env_vars['OPENSEARCH_COOKIES'] = f'"{cookie_string}"'
    
    # Write back to .env file
    with open(env_path, 'w') as f:
        f.write("# OpenSearch MCP Server Configuration\n")
        f.write("# Auto-updated with Okta cookies\n\n")
        
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Updated {env_path} with new cookies")

def main():
    print("🔐 Okta Cookie Extraction Helper")
    print("=" * 40)
    
    # Configuration
    opensearch_url = input("Enter OpenSearch Dashboards URL: ").strip()
    if not opensearch_url:
        opensearch_url = "https://opensearch.company.com"
    
    print("\nAuthentication options:")
    print("1. Manual login (recommended)")
    print("2. Automated login (username/password)")
    
    choice = input("Choose option (1/2): ").strip()
    
    okta_username = None
    okta_password = None
    
    if choice == "2":
        okta_username = input("Okta username: ").strip()
        okta_password = input("Okta password: ").strip()
        print("⚠️  Note: MFA will still require manual intervention")
    
    # Extract cookies
    cookies = extract_okta_cookies(
        opensearch_url, 
        okta_username, 
        okta_password,
        headless=False  # Show browser for manual intervention
    )
    
    if cookies:
        # Format cookies
        cookie_string = format_cookies_for_env(cookies)
        
        print(f"\n📋 Cookie string for .env file:")
        print(f'OPENSEARCH_COOKIES="{cookie_string}"')
        
        # Save options
        print(f"\n💾 Save options:")
        print(f"1. Update .env file automatically")
        print(f"2. Save to cookies.txt file")
        print(f"3. Display only (manual copy)")
        
        save_choice = input("Choose option (1/2/3): ").strip()
        
        if save_choice == "1":
            update_env_file(cookie_string)
        elif save_choice == "2":
            save_cookies_to_file(cookies)
        
        print(f"\n✅ Cookie extraction completed!")
        print(f"💡 Test with: python test_cookie_auth.py")
        
    else:
        print(f"\n❌ No cookies extracted. Please try again.")

if __name__ == "__main__":
    main()