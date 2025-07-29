import os
from dataclasses import dataclass
from datetime import timedelta
from dotenv import load_dotenv

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
    
    @property
    def timeout_seconds(self) -> float:
        return self.timeout.total_seconds()
    
    @property
    def url(self) -> str:
        protocol = "https" if self.use_ssl else "http"
        return f"{protocol}://{self.host}:{self.port}"

# Create a single instance to import elsewhere
opensearch_config = OpenSearchConfig()