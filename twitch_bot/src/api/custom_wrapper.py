"""
Custom Twitch API wrapper to bypass TwitchIO's parameter bug.
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any


class CustomTwitchAPI:
    """Custom wrapper for Twitch API calls."""
    
    def __init__(self, client_id: str, access_token: str):
        """Initialize the API wrapper.
        
        Args:
            client_id: Twitch application client ID
            access_token: OAuth access token
        """
        self.client_id = client_id
        self.access_token = access_token
        self.base_url = "https://api.twitch.tv/helix"
        
    async def get_user_by_login(self, login: str) -> Optional[Dict[str, Any]]:
        """Get user information by username (login).
        
        Args:
            login: Twitch username
            
        Returns:
            User data dictionary or None if not found
        """
        url = f"{self.base_url}/users"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        # Use correct 'login' parameter instead of 'id'
        params = {"login": login}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        users = data.get("data", [])
                        return users[0] if users else None
                    else:
                        print(f"API call failed: {response.status}")
                        return None
            except Exception as e:
                print(f"Error fetching user {login}: {e}")
                return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user information by numeric ID.
        
        Args:
            user_id: Twitch user ID
            
        Returns:
            User data dictionary or None if not found
        """
        url = f"{self.base_url}/users"
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }
        
        # Use 'id' parameter for numeric IDs
        params = {"id": user_id}
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        users = data.get("data", [])
                        return users[0] if users else None
                    else:
                        print(f"API call failed: {response.status}")
                        return None
            except Exception as e:
                print(f"Error fetching user {user_id}: {e}")
                return None