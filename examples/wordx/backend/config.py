#!/usr/bin/env python3
"""
Configuration management for WordX Backend
"""

import os
from pathlib import Path
from typing import Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings

class WordXConfig(BaseSettings):
    """WordX Backend Configuration"""
    
    # Server settings
    backend_host: str = "0.0.0.0"
    backend_port: int = 8765  # Unique port for WordX backend
    addon_port: int = 3456    # Unique port for WordX addon
    
    # Development vs Production
    environment: str = "development"
    debug: bool = True
    
    # CORS settings
    cors_origins: Optional[list] = None
    
    # AgentX settings
    agentx_config_path: Optional[str] = None
    
    # API settings
    api_timeout: int = 300  # 5 minutes
    
    # Task settings
    max_active_tasks: int = 100
    task_cleanup_interval: int = 3600  # 1 hour
    
    class Config:
        env_prefix = "WORDX_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from .env file
    
    def get_cors_origins(self) -> list:
        """Get CORS origins based on environment"""
        if self.cors_origins:
            return self.cors_origins
            
        if self.environment == "production":
            # In production, you'd specify exact origins
            return [
                "https://yourdomain.com",
                # Add your production Office 365 domains
            ]
        else:
            # Development origins
            return [
                f"https://localhost:{self.addon_port}",
                f"http://localhost:{self.addon_port}",
                "https://localhost:8080",  # Default Office.js debugging
            ]
    
    def get_agentx_config_path(self) -> Path:
        """Get the AgentX configuration file path"""
        if self.agentx_config_path:
            return Path(self.agentx_config_path)
        
        # Default to config/team.yaml relative to backend
        return Path(__file__).parent / "config" / "team.yaml"
        return Path(__file__).parent / "config" / "team.yaml"

# Global config instance
config = WordXConfig()