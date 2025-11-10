"""Configuration management for QueueCTL."""

from typing import Optional
from .storage import Storage


class Config:
    """Configuration manager for the queue system."""
    
    DEFAULT_CONFIG = {
        "max-retries": "3",
        "backoff-base": "2",
        "worker-count": "1",
        "job-timeout": "300",
    }
    
    def __init__(self, storage: Storage):
        """Initialize configuration manager."""
        self.storage = storage
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """Ensure default configuration values exist."""
        current_config = self.storage.get_all_config()
        for key, value in self.DEFAULT_CONFIG.items():
            if key not in current_config:
                self.storage.set_config(key, value)
    
    def get(self, key: str) -> Optional[str]:
        """Get configuration value."""
        value = self.storage.get_config(key)
        if value is None:
            return self.DEFAULT_CONFIG.get(key)
        return value
    
    def get_int(self, key: str) -> int:
        """Get configuration value as integer."""
        value = self.get(key)
        try:
            return int(value) if value else 0
        except ValueError:
            return 0
    
    def set(self, key: str, value: str):
        """Set configuration value."""
        # Validate known keys
        if key in self.DEFAULT_CONFIG:
            try:
                # Validate integer values
                int(value)
            except ValueError:
                raise ValueError(f"Configuration value for '{key}' must be an integer")
        
        self.storage.set_config(key, value)
    
    def get_all(self) -> dict:
        """Get all configuration values."""
        config = self.DEFAULT_CONFIG.copy()
        config.update(self.storage.get_all_config())
        return config
    
    def show(self) -> str:
        """Get formatted configuration display."""
        config = self.get_all()
        lines = ["Configuration", "─" * 40]
        for key, value in sorted(config.items()):
            lines.append(f"{key:20s}: {value}")
        return "\n".join(lines)
