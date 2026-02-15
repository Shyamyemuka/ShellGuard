"""
ShellGuard Configuration
"""
import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env from backend directory
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from: {env_path}")
else:
    print("⚠️  No .env file found at backend/.env")

class Settings(BaseSettings):
    # Application
    app_env: str = os.getenv("APP_ENV", "development")
    app_port: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))  # Render uses $PORT
    
    # LLM
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
    llm_fallback_model: str = os.getenv("LLM_FALLBACK_MODEL", "gemini-1.5-pro")
    llm_temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    llm_max_tokens: int = int(os.getenv("LLM_MAX_TOKENS", "800"))
    
    # Archestra
    archestra_api_key: str = os.getenv("ARCHESTRA_API_KEY", "")
    archestra_runtime_url: str = os.getenv("ARCHESTRA_RUNTIME_URL", "")
    archestra_project_id: str = os.getenv("ARCHESTRA_PROJECT_ID", "shellguard")
    archestra_observability_enabled: bool = os.getenv("ARCHESTRA_OBSERVABILITY_ENABLED", "true").lower() == "true"
    archestra_guardrails_enabled: bool = os.getenv("ARCHESTRA_GUARDRAILS_ENABLED", "true").lower() == "true"
    
    # Database
    database_path: str = os.getenv("DATABASE_PATH", "./data/shellguard.db")
    
    # Security
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    ws_idle_timeout: int = int(os.getenv("WS_IDLE_TIMEOUT_SECONDS", "1800"))
    
    # Sandbox (for safe demo deployment)
    sandbox_mode: bool = os.getenv("SANDBOX_MODE", "true").lower() == "true"
    sandbox_dir: str = os.getenv("SANDBOX_DIR", "/tmp/shellguard_sandbox")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"

settings = Settings()
