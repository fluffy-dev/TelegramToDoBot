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

    async def _request(self, method: str, path: str, **kwargs) -> Union[Dict[str, Any], None]:
        """
        Makes an asynchronous HTTP request.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST').
            path (str): The API endpoint path.

        Returns:
            A dictionary with the JSON response, or None for 204 status.
        """
        url = f"{self.base_url}{path}"
        async with ClientSession(headers=self.headers) as session:
            try:
                async with session.request(method, url, **kwargs) as response:
                    response.raise_for_status()
                    # Если ответ 204 No Content, возвращаем None
                    if response.status == 204:
                        return None
                    return await response.json()
            except ClientResponseError as e:
                # Добавим больше информации в лог для отладки
                error_body = await e.text()
                self.logger.error(f"API request failed: {e.status} {e.message} | Body: {error_body}")
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

    async def create_task(self, title: str, description: str, due_date: str, category_ids: list[str]) -> dict:
        """
        Creates a new task.

        Args:
            title: The title of the task.
            description: The description of the task.
            due_date: The due date in ISO format.
            category_ids: A list of category IDs to associate with the task.

        Returns:
            The created task data.
        """
        payload = {
            "title": title,
            "description": description,
            "due_date": due_date,
            "categories": category_ids
        }
        return await self._request("POST", "/tasks/", json=payload)

    async def get_task(self, task_id: str) -> dict:
        """Fetches a single task by its ID."""
        return await self._request("GET", f"/tasks/{task_id}/")

    async def delete_task(self, task_id: str) -> None:
        """Deletes a task by its ID."""
        await self._request("DELETE", f"/tasks/{task_id}/")

    async def update_task(self, task_id: str, payload: dict) -> dict:
        """
        Updates an existing task.

        Args:
            task_id: The ID of the task to update.
            payload: A dictionary with the data to update.

        Returns:
            The updated task data.
        """
        return await self._request("PUT", f"/tasks/{task_id}/", json=payload)

    async def patch_task(self, task_id: str, payload: dict) -> dict:
        """
        Partially updates an existing task using PATCH.

        Args:
            task_id: The ID of the task to update.
            payload: A dictionary with the fields to update.

        Returns:
            The updated task data.
        """
        return await self._request("PATCH", f"/tasks/{task_id}/", json=payload)