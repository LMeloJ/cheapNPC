"""
Configuration management for cheapNPC.

This module provides centralized configuration management with support for:
- Environment variables
- Configuration files
- Default values
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv(override=True)


class AIConfig(BaseModel):
    """AI Model configuration."""
    
    provider: str = Field(
        default="gemini",
        description="AI provider to use (gemini, openai, anthropic)"
    )
    
    model_name: str = Field(
        default="gemini-2.5-flash",
        description="Model name to use"
    )
    
    base_url: str = Field(
        default="https://generativelanguage.googleapis.com/v1beta/openai/",
        description="Base URL for the AI API"
    )
    
    api_key: str = Field(
        default="",
        description="API key for the AI service"
    )
    
    temperature: float = Field(
        default=0.7,
        description="Temperature for AI responses"
    )
    
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens for AI responses"
    )


class DatabaseConfig(BaseModel):
    """Database configuration."""
    
    path: str = Field(
        default="data/village.db",
        description="Path to the SQLite database file"
    )
    
    auto_create: bool = Field(
        default=True,
        description="Whether to automatically create the database if it doesn't exist"
    )


class ServerConfig(BaseModel):
    """Server configuration."""
    
    host: str = Field(
        default="0.0.0.0",
        description="Server host address"
    )
    
    port: int = Field(
        default=7861,
        description="Server port number"
    )
    
    share: bool = Field(
        default=False,
        description="Whether to create a public share link"
    )
    
    show_error: bool = Field(
        default=True,
        description="Whether to show errors in the UI"
    )


class Config(BaseModel):
    """Main configuration model."""
    
    ai: AIConfig = Field(default_factory=AIConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    
    # Project metadata
    project_name: str = Field(
        default="CheapNPC",
        description="Project name"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )


class ConfigManager:
    """Configuration manager singleton."""
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[Config] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._config = self._load_config()
    
    def _load_config(self) -> Config:
        """Load configuration from environment variables and defaults."""
        
        # AI Configuration
        ai_provider = os.getenv("AI_PROVIDER", "gemini").lower()
        ai_model = os.getenv("AI_MODEL", "gemini-2.5-flash")
        ai_base_url = os.getenv("AI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
        ai_temperature = float(os.getenv("AI_TEMPERATURE", "0.7"))
        
        # Get API key based on provider
        api_key = ""
        if ai_provider == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY", "")
        elif ai_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY", "")
        elif ai_provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
        
        # Database Configuration
        db_path = os.getenv("DATABASE_PATH", "data/village.db")
        db_auto_create = os.getenv("DATABASE_AUTO_CREATE", "true").lower() == "true"
        
        # Server Configuration
        server_host = os.getenv("SERVER_HOST", "0.0.0.0")
        server_port = int(os.getenv("SERVER_PORT", "7861"))
        server_share = os.getenv("SERVER_SHARE", "false").lower() == "true"
        server_show_error = os.getenv("SERVER_SHOW_ERROR", "true").lower() == "true"
        
        # Debug mode
        debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Build configuration
        config = Config(
            ai=AIConfig(
                provider=ai_provider,
                model_name=ai_model,
                base_url=ai_base_url,
                api_key=api_key,
                temperature=ai_temperature
            ),
            database=DatabaseConfig(
                path=db_path,
                auto_create=db_auto_create
            ),
            server=ServerConfig(
                host=server_host,
                port=server_port,
                share=server_share,
                show_error=server_show_error
            ),
            debug=debug
        )
        
        return config
    
    def get_config(self) -> Config:
        """Get the current configuration."""
        return self._config
    
    def reload(self):
        """Reload configuration from environment variables."""
        self._config = self._load_config()
    
    # Convenience methods for accessing configuration
    @property
    def ai(self) -> AIConfig:
        """Get AI configuration."""
        return self._config.ai
    
    @property
    def database(self) -> DatabaseConfig:
        """Get database configuration."""
        return self._config.database
    
    @property
    def server(self) -> ServerConfig:
        """Get server configuration."""
        return self._config.server


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get the current configuration."""
    return config_manager.get_config()
