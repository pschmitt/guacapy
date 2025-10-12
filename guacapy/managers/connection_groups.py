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
from .base import BaseManager
from ..utilities import requester, validate_payload

# Get the logger for this module
logger = logging.getLogger(__name__)

class ConnectionGroupManager(BaseManager):
    ORG_TEMPLATE: Dict[str, Any] = {
        "name": "",
        "parentIdentifier": "ROOT",
        "type": "ORGANIZATIONAL",
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
        },
    }

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
        super().__init__(client, datasource)
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

    def get_by_name(self, name: str, regex: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieve a connection group by its name.

        Parameters
        ----------
        name : str
            The name of the connection group to find.
        regex : bool, optional
            Whether to use regex matching for the name. Defaults to False.

        Returns
        -------
        Optional[Dict[str, Any]]
            The connection group dictionary if found, else None.

        Examples
        --------
        >>> group = group_manager.get_by_name("Root Group")
        >>> print(group)
        {'identifier': 'ROOT', 'name': 'Root Group', 'type': 'ORGANIZATIONAL', ...}
        """
        from ..utilities import _find_connection_group_by_name
        cons = self.list()
        return _find_connection_group_by_name(self.client, cons, name, regex)

    def create(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new connection group.

        Parameters
        ----------
        payload : Dict[str, Any]
            The connection group creation payload. Must conform to ORG_TEMPLATE.

        Returns
        -------
        Optional[Dict[str, Any]]
            The created connection group details, or None if the group already exists (400 error).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails for reasons other than 400.

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(ConnectionGroupManager.ORG_TEMPLATE)
        >>> payload.update({"name": "testgroup"})
        >>> group = group_manager.create(payload)
        """
        validate_payload(payload, self.ORG_TEMPLATE)
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
            The update payload. Must conform to ORG_TEMPLATE.

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
        >>> payload = deepcopy(ConnectionGroupManager.ORG_TEMPLATE)
        >>> payload.update({"name": "testgroup_updated", "identifier": "2"})
        >>> response = group_manager.update("2", payload)
        """
        validate_payload(payload, self.ORG_TEMPLATE)
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
