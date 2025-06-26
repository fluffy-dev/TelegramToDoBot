import logging
from typing import Optional, Dict, Any, Union

from aiohttp import ClientSession, ClientResponseError


class ApiClient:
    """
    An asynchronous client for interacting with the ToDo List API.
    """

    def __init__(self, base_url: str, token: Optional[str] = None):
        """
        Initializes the API client.

        Args:
            base_url (str): The base URL of the API.
            token (str, optional): The authentication token.
        """
        self.base_url = base_url
        self.headers = {}
        if token:
            self.headers['Authorization'] = f'Token {token}'
        self.logger = logging.getLogger(__name__)

    async def _request(self, method: str, path: str, **kwargs) -> Union[Dict[str, Any], list]:
        """
        Makes an asynchronous HTTP request.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            path (str): The API endpoint path.

        Returns:
            A dictionary with the JSON response.
        """
        url = f"{self.base_url}{path}"
        async with ClientSession(headers=self.headers) as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    return await response.json()
            except ClientResponseError as e:
                self.logger.error(f"API request failed: {e.status} {e.message}")
                raise

    async def authenticate(self, telegram_id: int, username: str) -> str:
        """
        Authenticates the user and retrieves an API token.

        Args:
            telegram_id (int): The user's Telegram ID.
            username (str): The user's Telegram username.

        Returns:
            The authentication token.
        """
        data = {"telegram_id": telegram_id, "username": username}
        response = await self._request("POST", "/users/auth/telegram/", json=data)
        return response.get("token")

    async def get_tasks(self) -> list:
        """Fetches the list of tasks."""
        return await self._request("GET", "/tasks/")

    async def get_categories(self) -> list:
        """Fetches the list of categories."""
        return await self._request("GET", "/categories/")