"""
User management module for the Guacamole REST API.

This module provides the `UserManager` class to interact with user-related endpoints of the
Apache Guacamole REST API, enabling operations such as listing users, retrieving user details,
managing permissions, group memberships, and connection history.

The API endpoints are based on the unofficial documentation for Guacamole version 1.1.0:
https://github.com/ridvanaltun/guacamole-rest-api-documentation

Parameters
----------
guac_client : Guacamole
    The Guacamole client instance with authentication details.
datasource : str, optional
    The data source identifier (e.g., 'mysql', 'postgresql'). Defaults to the client's primary data source.

Raises
------
requests.HTTPError
    If any API request fails (e.g., 401 for invalid credentials, 403 for insufficient permissions).

Examples
--------
Create a client and list users:
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="192.168.11.53", username="guacadmin", password="abAB12!@", connection_protocol="https", ssl_verify=False, connection_port=8443)
>>> user_manager = client.users
>>> users = user_manager.list()
>>> print(users)
{'guacadmin': {'username': 'guacadmin', 'disabled': False, 'attributes': {...}, 'lastActive': 1760229440000}, ...}

Retrieve user details:
>>> user = user_manager.user_details("daxm")
>>> print(user)
{'username': 'daxm', 'disabled': False, 'attributes': {'guac-full-name': 'Dax Mickelson', 'guac-email-address': 'asdf@asdf.com', ...}, 'lastActive': 1760023106000}
"""

import logging
import requests
from typing import Dict, Any, Optional
from ..utilities import requester

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
            The data source identifier (e.g., 'mysql', 'postgresql'). Defaults to
            guac_client.primary_datasource if None.

        Attributes
        ----------
        guac_client : Any
            The provided Guacamole client instance.
        datasource : str
            The data source identifier for API requests.
        url : str
            The base URL for user-related endpoints.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        self.guac_client = guac_client
        if datasource:
            self.datasource = datasource
        else:
            self.datasource = self.guac_client.primary_datasource
        self.url = (
            f"{self.guac_client.base_url}/session/data/{self.datasource}/users"
        )

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all users in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping usernames to user details, including attributes and last active time.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> users = user_manager.list()
        >>> print(users)
        {'guacadmin': {'username': 'guacadmin', 'disabled': False, 'attributes': {...}, 'lastActive': 1760229440000}, ...}
        """
        result = requester(
            guac_client=self.guac_client,
            url=self.url,
        )
        return result

    def user_details(self, username: str) -> Dict[str, Any]:
        """
        Retrieve details for a specific user.

        Parameters
        ----------
        username : str
            The username of the user to retrieve details for.

        Returns
        -------
        Dict[str, Any]
            The user details, including attributes and last active time.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 401 for unauthorized).

        Examples
        --------
        >>> user = user_manager.user_details("daxm")
        >>> print(user)
        {'username': 'daxm', 'disabled': False, 'attributes': {'guac-full-name': 'Dax Mickelson', 'guac-email-address': 'asdf@asdf.com', ...}, 'lastActive': 1760023106000}
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}",
        )
        return result

    def user_permissions(self, username: str) -> Dict[str, Any]:
        """
        Retrieve a user's explicit permissions.

        Parameters
        --------
        username : str
            The username of the user whose permissions are retrieved.

        Returns
        -------
        Dict[str, Any]
            The user's permissions, including system, connection, and group permissions.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 401 for unauthorized).

        Examples
        --------
        >>> permissions = user_manager.user_permissions("daxm")
        >>> print(permissions)
        {'connectionPermissions': {'1': ['READ']}, 'connectionGroupPermissions': {}, 'sharingProfilePermissions': {}, 'activeConnectionPermissions': {}, 'userPermissions': {'daxm': ['READ']}, 'userGroupPermissions': {}, 'systemPermissions': []}
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/permissions",
        )
        return result

    def user_effective_permissions(self, username: str) -> Dict[str, Any]:
        """
        Retrieve a user's effective permissions (inherited and explicit).

        Parameters
        ----------
        username : str
            The username of the user whose effective permissions are retrieved.

        Returns
        -------
        Dict[str, Any]
            The user's effective permissions, including system, connection, and group permissions.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 401 for unauthorized).

        Examples
        --------
        >>> effective_perms = user_manager.user_effective_permissions("daxm")
        >>> print(effective_perms)
        {'connectionPermissions': {'1': ['READ']}, 'connectionGroupPermissions': {}, 'sharingProfilePermissions': {}, 'activeConnectionPermissions': {}, 'userPermissions': {'daxm': ['READ']}, 'userGroupPermissions': {}, 'systemPermissions': []}
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/effectivePermissions",
        )
        return result

    def user_usergroups(self, username: str) -> Dict[str, Any]:
        """
        List the user groups a user belongs to.

        Parameters
        ----------
        username : str
            The username of the user whose user groups are retrieved.

        Returns
        -------
        Dict[str, Any]
            A list of user group identifiers.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 401 for unauthorized).

        Examples
        --------
        >>> groups = user_manager.user_usergroups("daxm")
        >>> print(groups)
        ['netadmins']
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/userGroups",
        )
        return result

    def user_history(self, username: str) -> Dict[str, Any]:
        """
        Retrieve connection history for a user.

        Parameters
        ----------
        username : str
            The username of the user whose connection history is retrieved.

        Returns
        -------
        Dict[str, Any]
            A list of connection history entries, each containing connection details and timestamps.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 401 for unauthorized).

        Examples
        --------
        >>> history = user_manager.user_history("daxm")
        >>> print(history)
        [{'identifier': '75', 'startDate': 1760023106000, 'uuid': '93b78545-...', 'remoteHost': '172.19.0.5', ...}, ...]
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}/history",
        )
        return result

    def assign_usergroups(
        self, username: str, usergroup: str
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 401 for unauthorized).

        Examples
        --------
        >>> response = user_manager.assign_usergroups("daxm", "netadmins")
        >>> print(response.status_code)
        204
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
        self, username: str, usergroup: str
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 401 for unauthorized).

        Examples
        --------
        >>> response = user_manager.revoke_usergroups("daxm", "netadmins")
        >>> print(response.status_code)
        204
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

    def self_details(self) -> Dict[str, Any]:
        """
        Retrieve details of the authenticated (token-owning) user.

        Returns
        -------
        Dict[str, Any]
            The authenticated user's details, including attributes and last active time.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized).

        Examples
        --------
        >>> user = user_manager.self_details()
        >>> print(user)
        {'username': 'guacadmin', 'disabled': False, 'attributes': {...}, 'lastActive': 1760229440000}
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent connection, 401 for unauthorized).

        Examples
        --------
        >>> response = user_manager.assign_connection("daxm", "1", permission="READ")
        >>> print(response.status_code)
        204
        """
        path = (
            "/connectionGroupPermissions"
            if is_connection_group
            else "/connectionPermissions"
        )
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent connection, 401 for unauthorized).

        Examples
        --------
        >>> response = user_manager.revoke_connection("daxm", "1", permission="READ")
        >>> print(response.status_code)
        204
        """
        path = (
            "/connectionGroupPermissions"
            if is_connection_group
            else "/connectionPermissions"
        )
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for invalid credentials, 403 for insufficient permissions).

        Examples
        --------
        >>> response = user_manager.update_password("daxm", "old_pass", "new_pass")
        >>> print(response.status_code)
        204
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

    def create(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new user.

        Parameters
        ----------
        payload : Dict[str, Any]
            The user creation payload containing username, password, and attributes.

        Returns
        -------
        Dict[str, Any]
            The created user details, including attributes and last active time.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 400 for invalid payload, 401 for unauthorized).

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
        >>> user = user_manager.create(payload)
        >>> print(user)
        {'username': 'test', 'disabled': False, 'attributes': {...}}
        """
        result = requester(
            guac_client=self.guac_client,
            url=self.url,
            method="POST",
            payload=payload,
        )
        return result

    def update(
        self, username: str, payload: Dict[str, Any]
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 400 for invalid payload).

        Examples
        --------
        >>> payload = {
        ...     "username": "daxm",
        ...     "attributes": {
        ...         "guac-email-address": "new@asdf.com",
        ...         "guac-organizational-role": null,
        ...         "guac-full-name": "Dax Mickelson",
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
        >>> response = user_manager.update("daxm", payload)
        >>> print(response.status_code)
        204
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}",
            method="PUT",
            payload=payload,
            json_response=False,
        )
        return result

    def delete(self, username: str) -> requests.Response:
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

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent user, 401 for unauthorized).

        Examples
        --------
        >>> response = user_manager.delete("daxm")
        >>> print(response.status_code)
        204
        """
        result = requester(
            guac_client=self.guac_client,
            url=f"{self.url}/{username}",
            method="DELETE",
            json_response=False,
        )
        return result
