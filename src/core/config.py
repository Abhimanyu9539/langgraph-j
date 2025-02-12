import os
from dotenv import load_dotenv

# Load environemntal variables
load_dotenv()


class Config:
    "Configurations for LLM"

    # API KEYS
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    SERPER_API_KEY = os.getenv("SERPER_API_KEY")


    # LLM Config
    LLM_MODEL = "gpt-4o-mini"
    LLM_TEMPERATURE = 0.1
    LLM_MAX_TOKENS = 10000

    # FILE Config
    MAX_FILE_SIZE_MB = 5
    ALLOWED_FILE_TYPES = [".pdf", ".docx", ".txt"]
    UPLOAD_DIR =  "uploads/"

    # Workflow Config
    MAX_JOBS_TO_FIND = 10
    MAX_JOBS_TO_SCORE = 10
    ENABLE_JOB_SEARCH = True
    
    # Job Seach Settings
    JOB_SEARCH_ENGINE  = "tavily"
    DEFAULT_LOCATION = "remote"