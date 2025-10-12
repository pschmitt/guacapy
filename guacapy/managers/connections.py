"""
Connection management module for the Guacamole REST API.

This module provides the `ConnectionManager` class to interact with connection endpoints of the
Apache Guacamole REST API, enabling operations such as listing connections, retrieving connection
details, creating, updating, and deleting connections.

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
Create a client and list connections:
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="192.168.11.53", username="guacadmin", password="abAB12!@", connection_protocol="https", ssl_verify=False, connection_port=8443)
>>> conn_manager = client.connections
>>> connections = conn_manager.list()
>>> print(connections)
{'1': {'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}}
"""

import logging
import requests
from typing import Dict, Any, Optional
from .base import BaseManager
from ..utilities import requester, validate_payload

# Get the logger for this module
logger = logging.getLogger(__name__)

class ConnectionManager(BaseManager):
    # Templates for common connection types
    RDP_TEMPLATE: Dict[str, Any] = {
        "name": "",
        "parentIdentifier": "ROOT",
        "protocol": "rdp",
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "weight": "",
            "failover-only": "",
            "guacd-port": "",
            "guacd-encryption": "",
            "guacd-hostname": "",
        },
        "parameters": {
            "hostname": "",
            "port": "3389",
            "username": "",
            "password": "",
            "security": "rdp",
            "disable-audio": "",
            "server-layout": "",
            "domain": "",
            "enable-font-smoothing": "",
            "ignore-cert": "",
            "console": "",
            "width": "",
            "height": "",
            "dpi": "",
            "color-depth": "",
            "console-audio": "",
            "enable-printing": "",
            "enable-drive": "",
            "create-drive-path": "",
            "enable-wallpaper": "",
            "enable-theming": "",
            "enable-full-window-drag": "",
            "enable-desktop-composition": "",
            "enable-menu-animations": "",
            "preconnection-id": "",
            "enable-sftp": "",
            "sftp-port": "",
        },
    }

    SSH_TEMPLATE: Dict[str, Any] = {
        "name": "",
        "parentIdentifier": "ROOT",
        "protocol": "ssh",
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
        },
        "parameters": {
            "hostname": "",
            "port": "22",
            "username": "",
            "password": "",
        },
    }

    VNC_TEMPLATE: Dict[str, Any] = {
        "name": "",
        "parentIdentifier": "ROOT",
        "protocol": "vnc",
        "attributes": {
            "max-connections": "",
            "max-connections-per-user": "",
            "weight": "",
            "failover-only": "",
            "guacd-port": "",
            "guacd-encryption": "",
            "guacd-hostname": "",
        },
        "parameters": {
            "hostname": "",
            "port": "5900",
            "password": "",
            "read-only": "",
            "swap-red-blue": "",
            "cursor": "",
            "color-depth": "",
            "clipboard-encoding": "",
            "dest-port": "",
            "create-recording-path": "",
            "enable-sftp": "",
            "sftp-port": "",
            "sftp-server-alive-interval": "",
            "enable-audio": "",
        },
    }

    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the ConnectionManager for interacting with Guacamole connection endpoints.

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
            The base URL for connection endpoints.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        super().__init__(client, datasource)
        self.url = (
            f"{self.client.base_url}/session/data/{self.datasource}/connections"
        )

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all connections in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping connection identifiers to their details.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> connections = conn_manager.list()
        >>> print(connections)
        {'1': {'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}}
        """
        result = requester(
            guac_client=self.client,
            url=self.url,
        )
        return result

    def details(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieve details for a specific connection.

        Parameters
        ----------
        identifier : str
            The identifier of the connection to retrieve details for.

        Returns
        -------
        Dict[str, Any]
            The connection details, including name, protocol, and parameters.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent connection, 401 for unauthorized).

        Examples
        --------
        >>> connection = conn_manager.details("1")
        >>> print(connection)
        {'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
        )
        return result

    def parameters(self, identifier: str) -> Dict[str, Any]:
        """
        Retrieve parameters for a specific connection.

        Parameters
        ----------
        identifier : str
            The identifier of the connection to retrieve parameters for.

        Returns
        -------
        Dict[str, Any]
            The connection parameters (e.g., hostname, port, username).

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent connection, 401 for unauthorized).

        Examples
        --------
        >>> params = conn_manager.parameters("1")
        >>> print(params)
        {'hostname': 'localhost', 'port': '22', 'username': 'admin', ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}/parameters",
        )
        return result

    def get_by_name(self, name: str, regex: bool = False) -> Optional[Dict[str, Any]]:
        """
        Retrieve a connection by its name.

        Parameters
        ----------
        name : str
            The name of the connection to find.
        regex : bool, optional
            Whether to use regex matching for the name. Defaults to False.

        Returns
        -------
        Optional[Dict[str, Any]]
            The connection dictionary if found, else None.

        Examples
        --------
        >>> connection = conn_manager.get_by_name("testconnection")
        >>> print(connection)
        {'identifier': '1', 'name': 'testconnection', 'protocol': 'ssh', ...}
        """
        from ..utilities import _find_connection_by_name
        cons = self.list()
        return _find_connection_by_name(self.client, cons, name, regex)

    def create(self, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new connection.

        Parameters
        ----------
        payload : Dict[str, Any]
            The connection creation payload. Must conform to one of the templates (e.g., RDP_TEMPLATE, SSH_TEMPLATE).

        Returns
        -------
        Optional[Dict[str, Any]]
            The created connection details, or None if the connection already exists (400 error).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails for reasons other than 400.

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(ConnectionManager.RDP_TEMPLATE)
        >>> payload.update({
        ...     "name": "testconnection",
        ...     "parameters": {"hostname": "localhost", "port": "3389"}
        ... })
        >>> connection = conn_manager.create(payload)
        """
        protocol = payload.get("protocol")
        if protocol == "rdp":
            validate_payload(payload, self.RDP_TEMPLATE)
        elif protocol == "ssh":
            validate_payload(payload, self.SSH_TEMPLATE)
        elif protocol == "vnc":
            validate_payload(payload, self.VNC_TEMPLATE)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
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
                    f"Failed to create connection {payload.get('name')} (already exists, 400)"
                )
                return None
            raise

    def update(
        self, identifier: str, payload: Dict[str, Any]
    ) -> requests.Response:
        """
        Update an existing connection.

        Parameters
        ----------
        identifier : str
            The identifier of the connection to update.
        payload : Dict[str, Any]
            The update payload. Must conform to one of the templates (e.g., RDP_TEMPLATE, SSH_TEMPLATE).

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent connection, 400 for invalid payload).

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(ConnectionManager.RDP_TEMPLATE)
        >>> payload.update({
        ...     "identifier": "2",
        ...     "name": "testconnection_updated",
        ...     "parameters": {"hostname": "localhost", "port": "3389"}
        ... })
        >>> response = conn_manager.update("2", payload)
        """
        protocol = payload.get("protocol")
        if protocol == "rdp":
            validate_payload(payload, self.RDP_TEMPLATE)
        elif protocol == "ssh":
            validate_payload(payload, self.SSH_TEMPLATE)
        elif protocol == "vnc":
            validate_payload(payload, self.VNC_TEMPLATE)
        else:
            raise ValueError(f"Unsupported protocol: {protocol}")
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
        Delete a connection.

        Parameters
        ----------
        identifier : str
            The identifier of the connection to delete.

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
        >>> response = conn_manager.delete("2")
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
