import os
from dataclasses import dataclass
from datetime import timedelta
from dotenv import load_dotenv
from typing import Dict, Optional

# Load environment variables from .env file
load_dotenv()

@dataclass
class OpenSearchConfig:
    host: str = os.getenv("OPENSEARCH_HOST", "localhost")
    port: int = int(os.getenv("OPENSEARCH_PORT", "9200"))
    username: str = os.getenv("OPENSEARCH_USERNAME", "")
    password: str = os.getenv("OPENSEARCH_PASSWORD", "")
    use_ssl: bool = os.getenv("OPENSEARCH_USE_SSL", "false").lower() == "true"
    verify_certs: bool = os.getenv("OPENSEARCH_VERIFY_CERTS", "false").lower() == "true"
    timeout: timedelta = timedelta(seconds=30)
    
    # Cookie authentication support
    use_cookies: bool = os.getenv("OPENSEARCH_USE_COOKIES", "false").lower() == "true"
    cookies: str = os.getenv("OPENSEARCH_COOKIES", "")
    cookie_file: str = os.getenv("OPENSEARCH_COOKIE_FILE", "")
    
    # Additional headers for authentication
    auth_headers: str = os.getenv("OPENSEARCH_AUTH_HEADERS", "")
    
    @property
    def timeout_seconds(self) -> float:
        return self.timeout.total_seconds()
    
    @property
    def url(self) -> str:
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"
    
    @property
    def parsed_cookies(self) -> Dict[str, str]:
        """Parse cookies from string format"""
        if not self.cookies:
            return {}
        
        cookies_dict = {}
        for cookie in self.cookies.split(';'):
            cookie = cookie.strip()
            if '=' in cookie:
                key, value = cookie.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
        return cookies_dict
    
    @property
    def parsed_auth_headers(self) -> Dict[str, str]:
        """Parse additional auth headers from string format"""
        if not self.auth_headers:
            return {}
        
        headers_dict = {}
        for header in self.auth_headers.split(','):
            header = header.strip()
            if ':' in header:
                key, value = header.split(':', 1)
                headers_dict[key.strip()] = value.strip()
        return headers_dict
    
    def load_cookies_from_file(self) -> Optional[Dict[str, str]]:
        """Load cookies from file if specified"""
        if not self.cookie_file or not os.path.exists(self.cookie_file):
            return None
        
        try:
            cookies_dict = {}
            with open(self.cookie_file, 'r') as f:
                content = f.read().strip()
                # Support both simple key=value format and Netscape cookie format
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            # Handle simple format: key=value
                            if line.count('\t') == 0:
                                key, value = line.split('=', 1)
                                cookies_dict[key.strip()] = value.strip()
                            else:
                                # Handle Netscape format: domain\tflag\tpath\tsecure\texpiration\tname\tvalue
                                parts = line.split('\t')
                                if len(parts) >= 7:
                                    cookies_dict[parts[5]] = parts[6]
            return cookies_dict
        except Exception as e:
            print(f"Warning: Could not load cookies from file {self.cookie_file}: {e}")
            return None

# Create a single instance to import elsewhere
opensearch_config = OpenSearchConfig()