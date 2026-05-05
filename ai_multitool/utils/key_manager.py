"""Secure API key management using system keyring."""

import os
from typing import Optional
from pathlib import Path

try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False


class KeyManager:
    """Secure API key manager using system keyring."""
    
    SERVICE_NAME = "ai-multitool"
    
    # Key identifiers
    ANTHROPIC_KEY = "anthropic_api_key"
    OPENAI_KEY = "openai_api_key"
    
    def __init__(self):
        """Initialize the key manager."""
        self.available = KEYRING_AVAILABLE
    
    def is_available(self) -> bool:
        """Check if keyring is available."""
        return self.available
    
    def set_key(self, key_id: str, value: str) -> bool:
        """Store an API key in the keyring."""
        if not self.available:
            return False
        
        try:
            keyring.set_password(self.SERVICE_NAME, key_id, value)
            return True
        except Exception as e:
            print(f"Error storing key in keyring: {e}")
            return False
    
    def get_key(self, key_id: str) -> Optional[str]:
        """Retrieve an API key from the keyring."""
        if not self.available:
            return None
        
        try:
            value = keyring.get_password(self.SERVICE_NAME, key_id)
            return value
        except Exception as e:
            print(f"Error retrieving key from keyring: {e}")
            return None
    
    def delete_key(self, key_id: str) -> bool:
        """Delete an API key from the keyring."""
        if not self.available:
            return False
        
        try:
            keyring.delete_password(self.SERVICE_NAME, key_id)
            return True
        except Exception as e:
            print(f"Error deleting key from keyring: {e}")
            return False
    
    def list_keys(self) -> list:
        """List all stored key IDs."""
        if not self.available:
            return []
        
        try:
            # Try to get known keys
            keys = []
            for key_id in [self.ANTHROPIC_KEY, self.OPENAI_KEY]:
                if self.get_key(key_id):
                    keys.append(key_id)
            return keys
        except Exception:
            return []
    
    def get_anthropic_key(self) -> Optional[str]:
        """Get Anthropic API key."""
        # Check keyring first
        key = self.get_key(self.ANTHROPIC_KEY)
        if key:
            return key
        
        # Fall back to environment variable
        return os.environ.get("ANTHROPIC_API_KEY")
    
    def get_openai_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        # Check keyring first
        key = self.get_key(self.OPENAI_KEY)
        if key:
            return key
        
        # Fall back to environment variable
        return os.environ.get("OPENAI_API_KEY")
    
    def set_anthropic_key(self, value: str) -> bool:
        """Set Anthropic API key."""
        return self.set_key(self.ANTHROPIC_KEY, value)
    
    def set_openai_key(self, value: str) -> bool:
        """Set OpenAI API key."""
        return self.set_key(self.OPENAI_KEY, value)
    
    def delete_anthropic_key(self) -> bool:
        """Delete Anthropic API key."""
        return self.delete_key(self.ANTHROPIC_KEY)
    
    def delete_openai_key(self) -> bool:
        """Delete OpenAI API key."""
        return self.delete_key(self.OPENAI_KEY)
    
    def migrate_from_env(self) -> dict:
        """Migrate keys from .env file to keyring."""
        migrated = {}
        
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_key and not self.get_anthropic_key():
            if self.set_anthropic_key(anthropic_key):
                migrated["anthropic"] = True
        
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key and not self.get_openai_key():
            if self.set_openai_key(openai_key):
                migrated["openai"] = True
        
        return migrated


# Singleton instance
_key_manager_instance: Optional[KeyManager] = None


def get_key_manager() -> KeyManager:
    """Get the singleton key manager instance."""
    global _key_manager_instance
    if _key_manager_instance is None:
        _key_manager_instance = KeyManager()
    return _key_manager_instance
