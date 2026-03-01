"""
OAuth authentication flow for Twitch API.
"""

import json
import time
from typing import Optional, Dict, Any
import requests
from ..exceptions.bot_exceptions import AuthenticationError


class OAuthManager:
    """Manages OAuth authentication and token refresh for Twitch API."""
    
    def __init__(self, client_id: str, client_secret: str):
        """Initialize OAuth manager.
        
        Args:
            client_id: Twitch application client ID
            client_secret: Twitch application client secret
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_expires_at: float = 0
        
    def get_app_token(self) -> str:
        """Get application access token using client credentials flow.
        
        Returns:
            Access token for app-only authentication
            
        Raises:
            AuthenticationError: If unable to obtain access token
        """
        url = "https://id.twitch.tv/oauth2/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Set expiration time (typically 1 hour, minus a buffer)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = time.time() + (expires_in - 300)  # 5 min buffer
            
            return self.access_token
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Failed to obtain app token: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise AuthenticationError(f"Invalid response from token endpoint: {e}")
    
    def get_user_token(self, authorization_code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for user access token.
        
        Args:
            authorization_code: Code received from OAuth redirect
            redirect_uri: Redirect URI used in the original request
            
        Returns:
            Dictionary containing token information
            
        Raises:
            AuthenticationError: If unable to exchange code for token
        """
        url = "https://id.twitch.tv/oauth2/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": authorization_code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            
            # Set expiration time
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = time.time() + (expires_in - 300)  # 5 min buffer
            
            return token_data
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Failed to exchange code for token: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise AuthenticationError(f"Invalid response from token endpoint: {e}")
    
    def refresh_user_token(self) -> str:
        """Refresh the user access token using refresh token.
        
        Returns:
            New access token
            
        Raises:
            AuthenticationError: If unable to refresh token
        """
        if not self.refresh_token:
            raise AuthenticationError("No refresh token available")
            
        url = "https://id.twitch.tv/oauth2/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            
            # Update refresh token if provided
            if "refresh_token" in token_data:
                self.refresh_token = token_data["refresh_token"]
            
            # Set new expiration time
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = time.time() + (expires_in - 300)  # 5 min buffer
            
            return self.access_token
            
        except requests.RequestException as e:
            raise AuthenticationError(f"Failed to refresh token: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise AuthenticationError(f"Invalid response from token refresh endpoint: {e}")
    
    def is_token_expired(self) -> bool:
        """Check if the current access token is expired or will expire soon.
        
        Returns:
            True if token is expired or expires within 5 minutes
        """
        return time.time() >= self.token_expires_at
    
    def get_valid_token(self) -> str:
        """Get a valid access token, refreshing if necessary.
        
        Returns:
            Valid access token
            
        Raises:
            AuthenticationError: If unable to obtain valid token
        """
        if not self.access_token or self.is_token_expired():
            if self.refresh_token:
                return self.refresh_user_token()
            else:
                return self.get_app_token()
        
        return self.access_token
    
    def get_authorization_url(self, redirect_uri: str, scopes: list = None) -> str:
        """Generate the OAuth authorization URL.
        
        Args:
            redirect_uri: Redirect URI for the application
            scopes: List of required scopes
            
        Returns:
            Authorization URL string
        """
        if not scopes:
            scopes = [
                "chat:read",
                "chat:edit",
                "user:read:email"
            ]
        
        scopes_str = "+".join(scopes)
        
        url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?response_type=code"
            f"&client_id={self.client_id}"
            f"&redirect_uri={requests.utils.quote(redirect_uri)}"
            f"&scope={scopes_str}"
        )
        
        return url