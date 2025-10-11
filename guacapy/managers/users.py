import logging
import requests
from utilities import requester
from typing import Dict, List, Any, Optional

# Get the logger for this module
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(
        self,
        client,
        datasource: Optional[str] = None,
    ):
        self.client = client
        if datasource:
            self.datasource = datasource
        else:
            self.datasource = self.client.primary_datasource
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/users"

    def list(self) -> dict:
        """Retrieve a list of all users in the datasource."""
        result = requester(
            client=self.client,
            url=self.url,
        )
        return result

    def user_details(
        self,
        username: str,
    ) -> requests.Response:
        """Retrieve details for a specific user."""
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}",
        )
        return result

    def user_permissions(
        self,
        username: str,
    ) -> requests.Response:
        """Retrieve a user's explicit permissions."""
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/permissions",
        )
        return result

    def user_effective_permissions(
        self,
        username: str,
    ) -> requests.Response:
        """Retrieve a user's effective permissions (inherited + explicit)."""
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/effectivePermissions",
        )
        return result

    def user_usergroups(
        self,
        username: str,
    ) -> requests.Response:
        """List the usergroups a user belongs to."""
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/userGroups",
        )
        return result

    def user_history(
        self,
        username: str,
    ) -> requests.Response:
        """Details of user history."""
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/history",
        )
        return result

    def assign_usergroups(
        self,
        username: str,
        usergroup: str,
    ) -> requests.Response:
        """
        Add user to a usergroup.

        :param username: str
        :param usergroup: str
        :return: requests.Response
        """
        payload = [
            {
                "op": "add",
                "path": "/",
                "value": usergroup,
            }
        ]
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/userGroups",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def revoke_usergroups(
        self,
        username: str,
        usergroup: str,
    ) -> requests.Response:
        """
        Remove user from a usergroup.

        :param username: str
        :param usergroup: str
        :return: requests.Response
        """
        payload = [
            {
                "op": "remove",
                "path": "/",
                "value": usergroup,
            }
        ]
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/userGroups",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def self_details(self) -> requests.Response:
        """
        Retrieve details of the authenticated (token-owning) user.

        :return: requests.Response (200 OK)
        """
        result = requester(
            client=self.client,
            url=f"{self.client.base_url}/session/data/{self.datasource}/self",
        )
        return result

    def assign_connection(
        self,
        username: str,
        connection_id: str,
        permission: str = "READ",
        is_connection_group: bool = False,
    ) -> requests.Response:
        """
        Assign a user to a connection or connection group with a specific permission.

        :param username: The username
        :param connection_id: The connection or connection group ID
        :param permission: The permission type (e.g., "READ", "WRITE", "ADMINISTER"). Defaults to "READ"
        :param is_connection_group: Set to True if assigning to a connection group. Defaults to False
        :return: requests.Response (204 No Content)
        """
        path = "/connectionGroupPermissions" if is_connection_group else "/connectionPermissions"
        payload = [
            {
                "op": "add",
                "path": f"{path}/{connection_id}",
                "value": permission,
            }
        ]
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/permissions",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def revoke_connection(
        self,
        username: str,
        connection_id: str,
        permission: str = "READ",
        is_connection_group: bool = False,
    ) -> requests.Response:
        """
        Revoke a user from a connection or connection group.

        :param username: The username
        :param connection_id: The connection or connection group ID
        :param permission: The permission type to revoke (e.g., "READ", "WRITE", "ADMINISTER"). Defaults to "READ"
        :param is_connection_group: Set to True if revoking from a connection group. Defaults to False
        :return: requests.Response (204 No Content)
        """
        path = "/connectionGroupPermissions" if is_connection_group else "/connectionPermissions"
        payload = [
            {
                "op": "remove",
                "path": f"{path}/{connection_id}",
                "value": permission,
            }
        ]
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/permissions",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def update_password(
        self,
        username: str,
        old_password: str,
        new_password: str,
    ) -> requests.Response:
        """
        Update a user's password.

        :param username: The username
        :param old_password: The current password
        :param new_password: The new password
        :return: requests.Response (204 No Content)
        """
        payload = {
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/password",
            method="PUT",
            payload=payload,
            json_response=False,
        )
        return result

    def create(
        self,
        payload: Dict[str, Any],
    ) -> requests.Response:
        """
        Create a new user.

        :param payload: User creation payload
            Example:
            {
                "username": "test",
                "password": "pass",
                "attributes": {
                    "disabled": "",
                    "expired": "",
                    "access-window-start": "",
                    "access-window-end": "",
                    "valid-from": "",
                    "valid-until": "",
                    "timezone": null,
                    "guac-full-name": "",
                    "guac-organization": "",
                    "guac-organizational-role": ""
                }
            }
        :return: requests.Response (200 OK)
        """
        result = requester(
            client=self.client,
            url=self.url,
            method="POST",
            payload=payload,
        )
        return result

    def update(
        self,
        username: str,
        payload: Dict[str, Any],
    ) -> requests.Response:
        """
        Update an existing user.

        :param username: The username to update
        :param payload: Update payload
            Example:
            {
                "username": "{{username}}",
                "attributes": {
                    "guac-email-address": null,
                    "guac-organizational-role": null,
                    "guac-full-name": null,
                    "expired": "",
                    "timezone": null,
                    "access-window-start": "",
                    "guac-organization": null,
                    "access-window-end": "",
                    "disabled": "",
                    "valid-until": "",
                    "valid-from": ""
                }
            }
        :return: requests.Response (204 No Content)
        """
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}",
            method="PUT",
            payload=payload,
            json_response=False,
        )
        return result

    def delete(
        self,
        username: str,
    ) -> requests.Response:
        """
        Delete a user.

        :param username: The username
        :return: requests.Response (204 No Content)
        """
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}",
            method="DELETE",
            json_response=False,
        )
        return result