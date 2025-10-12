"""
User group management module for the Guacamole REST API.

This module provides the `UserGroupManager` class to interact with user group endpoints of the
Apache Guacamole REST API, enabling operations such as listing user groups, retrieving group
details, creating, updating, and deleting user groups.

The API endpoints are based on the unofficial documentation for Guacamole version 1.1.0:
https://github.com/ridvanaltun/guacamole-rest-api-documentation

Parameters
----------
client : Guacamole
    The Guacamole client instance with authentication details.
datasource : str, optional
    The data source identifier (e.g., 'mysql', 'postgresql'). Defaults to the client's primary data source.

Examples
--------
Create a client and list user groups:
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="192.168.11.53", username="guacadmin", password="abAB12!@", connection_protocol="https", ssl_verify=False, connection_port=8443)
>>> group_manager = client.user_groups
>>> groups = group_manager.list()
>>> print(groups)
{'netadmins': {'identifier': 'netadmins', 'disabled': False, 'attributes': {}}, 'sysadmins': {...}}
"""

import logging
import requests
from typing import Dict, Any, Optional, List
from .base import BaseManager
from ..utilities import requester, validate_payload

# Get the logger for this module
logger = logging.getLogger(__name__)

class UserGroupManager(BaseManager):
    GROUP_TEMPLATE: Dict[str, Any] = {
        "identifier": "",
        "attributes": {"disabled": ""},
    }

    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the UserGroupManager for interacting with Guacamole user group endpoints.

        Parameters
        ----------
        client : Any
            The Guacamole client instance with base_url and authentication details.
        datasource : Optional[str], optional
            The data source identifier (e.g., 'mysql', 'postgresql'). Defaults to
            client.primary_datasource if None.

        Attributes
        ----------
        client : Any
            The provided Guacamole client instance.
        datasource : str
            The data source identifier for API requests.
        url : str
            The base URL for user group endpoints.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        super().__init__(client, datasource)
        self.url = (
            f"{self.client.base_url}/session/data/{self.datasource}/userGroups"
        )

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all user groups in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping user group identifiers to their details.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> groups = group_manager.list()
        >>> print(groups)
        {'netadmins': {'identifier': 'netadmins', 'disabled': False, 'attributes': {}}, 'sysadmins': {...}}
        """
        result = requester(
            guac_client=self.client,
            url=self.url,
        )
        return result

    def details(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieve details for a specific user group.

        Parameters
        ----------
        identifier : str
            The identifier of the user group to retrieve details for.

        Returns
        -------
        Dict[str, Any]
            The user group details, including attributes and permissions.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 401 for unauthorized).

        Examples
        --------
        >>> group = group_manager.details("netadmins")
        >>> print(group)
        {'identifier': 'netadmins', 'attributes': {'disabled': False}, ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
        )
        return result

    def members(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieve member users of a specific user group.

        Parameters
        ----------
        identifier : str
            The identifier of the user group to retrieve members for.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping usernames to user details for group members.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 401 for unauthorized).

        Examples
        --------
        >>> members = group_manager.members("netadmins")
        >>> print(members)
        {'daxm': {'username': 'daxm', 'attributes': {...}, ...}, ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}/memberUsers",
        )
        return result

    def edit_members(self, identifier: str, payload: List[Dict[str, Any]]) -> requests.Response:
        """
        Add or remove members from a user group.

        Parameters
        ----------
        identifier : str
            The identifier of the user group to modify.
        payload : List[Dict[str, Any]]
            The patch payload to add or remove members.
            Example: [{"op": "add", "path": "/", "value": "username"}]

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
        >>> payload = [{"op": "add", "path": "/", "value": "daxm"}]
        >>> response = group_manager.edit_members("netadmins", payload)
        >>> print(response.status_code)
        204
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}/memberUsers",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def create(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new user group.

        Parameters
        ----------
        payload : Dict[str, Any]
            The user group creation payload. Must conform to GROUP_TEMPLATE.

        Returns
        -------
        Optional[Dict[str, Any]]
            The created user group details, or None if the group already exists (400 error).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails for reasons other than 400.

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(UserGroupManager.GROUP_TEMPLATE)
        >>> payload.update({"identifier": "testgroup"})
        >>> group = group_manager.create(payload)
        """
        validate_payload(payload, self.GROUP_TEMPLATE)
        try:
            result = requester(
                guac_client=self.client,
                url=self.url,
                method="POST",
                payload=payload,
            )
            return result
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                logger.warning(
                    f"Failed to create user group {payload.get('identifier')} (already exists, 400)"
                )
                return None
            raise

    def update(
        self, identifier: str, payload: Dict[str, Any]
    ) -> requests.Response:
        """
        Update an existing user group.

        Parameters
        ----------
        identifier : str
            The identifier of the user group to update.
        payload : Dict[str, Any]
            The update payload. Must conform to GROUP_TEMPLATE.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 400 for invalid payload).

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(UserGroupManager.GROUP_TEMPLATE)
        >>> payload.update({"identifier": "testgroup", "attributes": {"disabled": True}})
        >>> response = group_manager.update("testgroup", payload)
        """
        validate_payload(payload, self.GROUP_TEMPLATE)
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
            method="PUT",
            payload=payload,
            json_response=False,
        )
        return result

    def delete(self, identifier: str) -> Optional[requests.Response]:
        """
        Delete a user group.

        Parameters
        ----------
        identifier : str
            The identifier of the user group to delete.

        Returns
        -------
        Optional[requests.Response]
            The HTTP response indicating success (204 No Content).
            Returns None if the deletion fails due to server error (500).

        Raises
        ------
        requests.HTTPError
            If the API request fails for reasons other than 500 (e.g., 404 for non-existent group, 401 for unauthorized).

        Examples
        --------
        >>> response = group_manager.delete("testgroup")
        >>> print(response.status_code)
        204
        >>> # If deletion fails due to server error
        >>> print(response)
        None

        Notes
        -----
        Deletion may fail with 500 due to SQL syntax error in Guacamole's MySQL JDBC module
        (missing AND in query: DELETE FROM guacamole_entity WHERE type = 'USER_GROUP' name = ?).
        Workaround: Manually delete via SQL: DELETE FROM guacamole_entity WHERE type = 'USER_GROUP' AND name = 'testgroup'.
        Reported to Guacamole team (GUACAMOLE-2088).
        """
        try:
            result = requester(
                guac_client=self.client,
                url=f"{self.url}/{identifier}",
                method="DELETE",
                json_response=False,
            )
            return result
        except requests.HTTPError as e:
            if e.response.status_code == 500:
                logger.warning(
                    f"Failed to delete user group {identifier} due to server error (500)"
                )
                return None
            raise
