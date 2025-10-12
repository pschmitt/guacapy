"""
Connection group management module for the Guacamole REST API.

This module provides the `ConnectionGroupManager` class to interact with connection group endpoints
of the Apache Guacamole REST API, enabling operations such as listing connection groups, retrieving
group details, creating, updating, and deleting connection groups.

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
Create a client and list connection groups:
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="192.168.11.53", username="guacadmin", password="abAB12!@", connection_protocol="https", ssl_verify=False, connection_port=8443)
>>> group_manager = client.connection_groups
>>> groups = group_manager.list()
>>> print(groups)
{'ROOT': {'identifier': 'ROOT', 'name': 'ROOT', 'type': 'ORGANIZATIONAL', ...}}
"""

import logging
import requests
from typing import Dict, Any, Optional
from ..utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class ConnectionGroupManager:
    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the ConnectionGroupManager for interacting with Guacamole connection group endpoints.

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
            The base URL for connection group endpoints.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        self.client = client
        if datasource:
            self.datasource = datasource
        else:
            self.datasource = self.client.primary_datasource
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/connectionGroups"

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all connection groups in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping connection group identifiers to their details.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> groups = group_manager.list()
        >>> print(groups)
        {'ROOT': {'identifier': 'ROOT', 'name': 'ROOT', 'type': 'ORGANIZATIONAL', ...}}
        """
        result = requester(
            guac_client=self.client,
            url=self.url,
        )
        return result

    def details(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieve details for a specific connection group.

        Parameters
        ----------
        identifier : str
            The identifier of the connection group to retrieve details for.

        Returns
        -------
        Dict[str, Any]
            The connection group details, including name, type, and child connections.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 401 for unauthorized).

        Examples
        --------
        >>> group = group_manager.details("ROOT")
        >>> print(group)
        {'identifier': 'ROOT', 'name': 'ROOT', 'type': 'ORGANIZATIONAL', ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
        )
        return result

    def create(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new connection group.

        Parameters
        ----------
        payload : Dict[str, Any]
            The connection group creation payload containing name and type.

        Returns
        -------
        Optional[Dict[str, Any]]
            The created connection group details, or None if the group already exists (400 error).

        Raises
        ------
        requests.HTTPError
            If the API request fails for reasons other than 400 (e.g., 401 for unauthorized).

        Examples
        --------
        >>> payload = {
        ...     "name": "testgroup",
        ...     "parentIdentifier": "ROOT",
        ...     "type": "ORGANIZATIONAL",
        ...     "attributes": {}
        ... }
        >>> group = group_manager.create(payload)
        >>> print(group)
        {'identifier': '2', 'name': 'testgroup', 'type': 'ORGANIZATIONAL', ...}
        >>> # If group already exists
        >>> print(group)
        None
        """
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
                    f"Failed to create connection group {payload.get('name')} (already exists, 400)"
                )
                return None
            raise

    def update(
        self, identifier: str, payload: Dict[str, Any]
    ) -> requests.Response:
        """
        Update an existing connection group.

        Parameters
        ----------
        identifier : str
            The identifier of the connection group to update.
        payload : Dict[str, Any]
            The update payload containing connection group attributes.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent group, 400 for invalid payload).

        Examples
        --------
        >>> payload = {
        ...     "identifier": "2",
        ...     "name": "testgroup_updated",
        ...     "parentIdentifier": "ROOT",
        ...     "type": "ORGANIZATIONAL",
        ...     "attributes": {}
        ... }
        >>> response = group_manager.update("2", payload)
        >>> print(response.status_code)
        204
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
            method="PUT",
            payload=payload,
            json_response=False,
        )
        return result

    def delete(self, identifier: str) -> requests.Response:
        """
        Delete a connection group.

        Parameters
        ----------
        identifier : str
            The identifier of the connection group to delete.

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
        >>> response = group_manager.delete("2")
        >>> print(response.status_code)
        204
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
            method="DELETE",
            json_response=False,
        )
        return result
