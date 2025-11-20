import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for RarePath AI"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
    
    # Model Configuration
    MODEL_NAME = "gemini-2.0-flash-001"  # Use stable Gemini 2.0 Flash model
    MAX_TOKENS = 8192
    TEMPERATURE = 0.7
    
    # Retry Configuration
    MAX_RETRIES = 3
    INITIAL_RETRY_DELAY = 1.0
    MAX_RETRY_DELAY = 60.0
    
    # Rate Limiting (calls per minute)
    RATE_LIMIT_CALLS_PER_MINUTE = 10
    
    # Search Parameters
    PUBMED_MAX_RESULTS = 20
    CLINICAL_TRIALS_MAX_RESULTS = 10
    SPECIALIST_SEARCH_RADIUS_MILES = 50
    
    # System Prompts
    SYSTEM_PROMPT = """You are RarePath AI, an expert medical assistant specializing in rare disease diagnosis support. 
    You help patients aggregate their symptoms, search medical literature, and connect with specialists.
    Always maintain a compassionate, clear, and professional tone. Never provide definitive diagnoses - only suggestions for discussion with healthcare providers."""
