import os
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
DOCUMENTS_DIR = DATA_DIR / "documents"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

# Create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini")
AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

# Validate required environment variables
if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY:
    print("⚠️  WARNING: Azure OpenAI credentials not found in .env file")

# Model settings
TEMPERATURE = 0.1
MAX_TOKENS = 1500
TOP_K_RESULTS = 5
EMBEDDING_DIMENSION = 1536  

# Approval thresholds (in IDR)
MANAGER_APPROVAL_LIMIT = 500_000_000
DIRECTOR_APPROVAL_LIMIT = 1_000_000_000

# Tax rate
VAT_RATE = 0.11