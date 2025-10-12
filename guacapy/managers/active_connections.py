"""
Active connection management module for the Guacamole REST API.

This module provides the `ActiveConnectionManager` class to interact with active connection
endpoints of the Apache Guacamole REST API, enabling operations such as listing active
connections, retrieving connection details, and terminating active connections.

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
Create a client and list active connections:
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="192.168.11.53", username="guacadmin", password="abAB12!@", connection_protocol="https", ssl_verify=False, connection_port=8443)
>>> active_conns = client.active_connections
>>> connections = active_conns.list()
>>> print(connections)
{}  # Empty if no active connections
"""

import logging
import requests
from typing import Dict, Any, Optional
from ..utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class ActiveConnectionManager:
    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the ActiveConnectionManager for interacting with Guacamole active connection endpoints.

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
            The base URL for active connection endpoints.

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
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/activeConnections"

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all active connections in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping connection identifiers to details, including start date, remote host, and username.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> connections = active_connection_manager.list()
        >>> print(connections)
        {}  # Empty if no active connections
        >>> # Example with active connection
        >>> print(connections)
        {'1': {'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', 'username': 'daxm', ...}}
        """
        result = requester(
            guac_client=self.client,
            url=self.url,
        )
        return result

    def details(self, identifier: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve details for a specific active connection.

        Parameters
        ----------
        identifier : str
            The identifier of the active connection to retrieve details for.

        Returns
        -------
        Optional[Dict[str, Any]]
            The active connection details, including start date, remote host, and username.
            Returns None if the connection is not active (404 error).

        Raises
        ------
        requests.HTTPError
            If the API request fails for reasons other than 404 (e.g., 401 for unauthorized).

        Examples
        --------
        >>> connection = active_connection_manager.details("1")
        >>> print(connection)
        {'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', 'username': 'daxm', ...}
        >>> # If connection is not active
        >>> print(connection)
        None
        """
        try:
            result = requester(
                guac_client=self.client,
                url=f"{self.url}/{identifier}",
            )
            return result
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(
                    f"Active connection {identifier} not found (404)"
                )
                return None
            raise

    def kill(self, identifier: str) -> Optional[requests.Response]:
        """
        Terminate an active connection.

        Parameters
        ----------
        identifier : str
            The identifier of the active connection to terminate.

        Returns
        -------
        Optional[requests.Response]
            The HTTP response indicating success (204 No Content).
            Returns None if the connection is not active (404 error).

        Raises
        ------
        requests.HTTPError
            If the API request fails for reasons other than 404 (e.g., 401 for unauthorized).

        Examples
        --------
        >>> response = active_connection_manager.kill("1")
        >>> print(response.status_code)
        204
        >>> # If connection is not active
        >>> print(response)
        None
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
            if e.response.status_code == 404:
                logger.warning(
                    f"Active connection {identifier} not found (404)"
                )
                return None
            raise
