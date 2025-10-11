"""
User management module for the Guacamole REST API.

This module provides the `UserManager` class to interact with user-related endpoints
of the Guacamole REST API, enabling operations such as creating, updating, deleting,
and querying user details, permissions, groups, and connection history.

Examples
--------
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="guacamole.example.com", username="admin", password="secret")
>>> user_manager = UserManager(client, datasource="mysql")
>>> response = user_manager.list()
>>> users = response  # Dictionary of users
"""

import logging
import requests
from utilities import requester
from typing import Dict, List, Any, Optional

# Get the logger for this module
logger = logging.getLogger(__name__)

class UserManager:
    def __init__(
        self,
        guac_client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the UserManager for interacting with Guacamole user endpoints.

        Parameters
        ----------
        guac_client : Any
            The Guacamole client instance with base_url and authentication details.
        datasource : Optional[str], optional
            The data source identifier. Defaults to guac_client.primary_datasource if None.
        """
        self.guac_client = guac_client
        if datasource:
            self.datasource = datasource
        else:
            self.datasource = self.guac_client.primary_datasource
        self.url = f"{self.guac_client.base_url}/session/data/{self.datasource}/users"

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all users in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the list of users (200 OK).

        Examples
        --------
        >>> user_manager.list()
        """
        result = requester(
            guac_client=self.guac_client,
            url=self.url,
        )
        return result

    def user_details(
        self,
        username: str,
    ) -> requests.Response:
        """
        Retrieve details for a specific user.

        Parameters
        ----------
        username : str
            The username of the user to retrieve details for.

        Returns
        -------
        requests.Response
            The HTTP response containing user details (200 OK).

        Examples
        --------
        >>> user_manager.user_details("john_doe")
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}",
        )
        return result

    def user_permissions(
        self,
        username: str,
    ) -> requests.Response:
        """
        Retrieve a user's explicit permissions.

        Parameters
        ----------
        username : str
            The username of the user whose permissions are retrieved.

        Returns
        -------
        requests.Response
            The HTTP response containing the user's permissions (200 OK).

        Examples
        --------
        >>> user_manager.user_permissions("john_doe")
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/permissions",
        )
        return result

    def user_effective_permissions(
        self,
        username: str,
    ) -> requests.Response:
        """
        Retrieve a user's effective permissions (inherited and explicit).

        Parameters
        ----------
        username : str
            The username of the user whose effective permissions are retrieved.

        Returns
        -------
        requests.Response
            The HTTP response containing the user's effective permissions (200 OK).

        Examples
        --------
        >>> user_manager.user_effective_permissions("john_doe")
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/effectivePermissions",
        )
        return result

    def user_usergroups(
        self,
        username: str,
    ) -> requests.Response:
        """
        List the user groups a user belongs to.

        Parameters
        ----------
        username : str
            The username of the user whose user groups are retrieved.

        Returns
        -------
        requests.Response
            The HTTP response containing the list of user groups (200 OK).

        Examples
        --------
        >>> user_manager.user_usergroups("john_doe")
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/userGroups",
        )
        return result

    def user_history(
        self,
        username: str,
    ) -> requests.Response:
        """
        Retrieve connection history for a user.

        Parameters
        ----------
        username : str
            The username of the user whose connection history is retrieved.

        Returns
        -------
        requests.Response
            The HTTP response containing the user's connection history (200 OK).

        Examples
        --------
        >>> user_manager.user_history("john_doe")
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/history",
        )
        return result

    def assign_usergroups(
        self,
        username: str,
        usergroup: str,
    ) -> requests.Response:
        """
        Add a user to a user group.

        Parameters
        ----------
        username : str
            The username of the user to add to the group.
        usergroup : str
            The identifier of the user group to add the user to.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> user_manager.assign_usergroups("john_doe", "admin_group")
        Payload sent:
        [
            {
                "op": "add",
                "path": "/",
                "value": "admin_group"
            }
        ]
        """
        payload = [
            {
                "op": "add",
                "path": "/",
                "value": usergroup,
            }
        ]
        result = requester(
            guac_client=self.guac_client,
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
        Remove a user from a user group.

        Parameters
        ----------
        username : str
            The username of the user to remove from the group.
        usergroup : str
            The identifier of the user group to remove the user from.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> user_manager.revoke_usergroups("john_doe", "admin_group")
        Payload sent:
        [
            {
                "op": "remove",
                "path": "/",
                "value": "admin_group"
            }
        ]
        """
        payload = [
            {
                "op": "remove",
                "path": "/",
                "value": usergroup,
            }
        ]
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/userGroups",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def self_details(self) -> requests.Response:
        """
        Retrieve details of the authenticated (token-owning) user.

        Returns
        -------
        requests.Response
            The HTTP response containing the authenticated user's details (200 OK).

        Examples
        --------
        >>> user_manager.self_details()
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.guac_client.base_url}/session/data/{self.datasource}/self",
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

        Parameters
        ----------
        username : str
            The username of the user to assign the permission to.
        connection_id : str
            The identifier of the connection or connection group.
        permission : str, optional
            The permission type (e.g., "READ", "WRITE", "ADMINISTER"). Defaults to "READ".
        is_connection_group : bool, optional
            Set to True if assigning to a connection group. Defaults to False.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> user_manager.assign_connection("john_doe", "conn_123", permission="READ")
        Payload sent:
        [
            {
                "op": "add",
                "path": "/connectionPermissions/conn_123",
                "value": "READ"
            }
        ]

        >>> user_manager.assign_connection("john_doe", "group_456", permission="READ", is_connection_group=True)
        Payload sent:
        [
            {
                "op": "add",
                "path": "/connectionGroupPermissions/group_456",
                "value": "READ"
            }
        ]
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
            guac_client=self.guac_client,
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

        Parameters
        ----------
        username : str
            The username of the user to revoke the permission from.
        connection_id : str
            The identifier of the connection or connection group.
        permission : str, optional
            The permission type to revoke (e.g., "READ", "WRITE", "ADMINISTER"). Defaults to "READ".
        is_connection_group : bool, optional
            Set to True if revoking from a connection group. Defaults to False.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> user_manager.revoke_connection("john_doe", "conn_123", permission="READ")
        Payload sent:
        [
            {
                "op": "remove",
                "path": "/connectionPermissions/conn_123",
                "value": "READ"
            }
        ]

        >>> user_manager.revoke_connection("john_doe", "group_456", permission="READ", is_connection_group=True)
        Payload sent:
        [
            {
                "op": "remove",
                "path": "/connectionGroupPermissions/group_456",
                "value": "READ"
            }
        ]
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
            guac_client=self.guac_client,
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

        Parameters
        ----------
        username : str
            The username of the user whose password is updated.
        old_password : str
            The current password of the user.
        new_password : str
            The new password to set.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> user_manager.update_password("john_doe", "old_pass", "new_pass")
        Payload sent:
        {
            "oldPassword": "old_pass",
            "newPassword": "new_pass"
        }
        """
        payload = {
            "oldPassword": old_password,
            "newPassword": new_password,
        }
        result = requester(
            guac_client=self.guac_client,
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

        Parameters
        ----------
        payload : Dict[str, Any]
            The user creation payload containing username, password, and attributes.

        Returns
        -------
        requests.Response
            The HTTP response containing the created user details (200 OK).

        Examples
        --------
        >>> payload = {
        ...     "username": "test",
        ...     "password": "pass",
        ...     "attributes": {
        ...         "disabled": "",
        ...         "expired": "",
        ...         "access-window-start": "",
        ...         "access-window-end": "",
        ...         "valid-from": "",
        ...         "valid-until": "",
        ...         "timezone": null,
        ...         "guac-full-name": "",
        ...         "guac-organization": "",
        ...         "guac-organizational-role": ""
        ...     }
        ... }
        >>> user_manager.create(payload)
        """
        result = requester(
            guac_client=self.guac_client,
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

        Parameters
        ----------
        username : str
            The username of the user to update.
        payload : Dict[str, Any]
            The update payload containing user attributes.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> payload = {
        ...     "username": "john_doe",
        ...     "attributes": {
        ...         "guac-email-address": null,
        ...         "guac-organizational-role": null,
        ...         "guac-full-name": null,
        ...         "expired": "",
        ...         "timezone": null,
        ...         "access-window-start": "",
        ...         "guac-organization": null,
        ...         "access-window-end": "",
        ...         "disabled": "",
        ...         "valid-until": "",
        ...         "valid-from": ""
        ...     }
        ... }
        >>> user_manager.update("john_doe", payload)
        """
        result = requester(
            guac_client=self.guac_client,
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

        Parameters
        ----------
        username : str
            The username of the user to delete.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Examples
        --------
        >>> user_manager.delete("john_doe")
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}",
            method="DELETE",
            json_response=False,
        )
        return result
