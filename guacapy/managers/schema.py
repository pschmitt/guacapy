"""
Schema management module for the Guacamole REST API.

This module provides the `SchemaManager` class to interact with schema-related endpoints
of the Apache Guacamole REST API, enabling operations such as retrieving supported
protocols and user attributes.

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
Create a client and list supported protocols:
>>> from guacapy import Guacamole
>>> client = Guacamole(hostname="192.168.11.53", username="guacadmin", password="abAB12!@", connection_protocol="https", ssl_verify=False, connection_port=8443)
>>> schema_manager = client.schema
>>> protocols = schema_manager.protocols()
>>> print(protocols)
{'ssh': {...}, 'rdp': {...}, ...}
"""

import logging
import requests
from typing import Dict, Any, Optional
from ..utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)

class SchemaManager:
    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the SchemaManager for interacting with Guacamole schema endpoints.

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
            The base URL for schema endpoints.

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
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/schema"

    def protocols(self) -> Dict[str, Any]:
        """
        Retrieve supported connection protocols.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping protocol names to their details.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> protocols = schema_manager.protocols()
        >>> print(protocols)
        {'ssh': {'name': 'ssh', 'attributes': {...}}, 'rdp': {...}, ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/protocols",
        )
        return result

    def user_attributes(self) -> Dict[str, Any]:
        """
        Retrieve available user attributes.

        Returns
        -------
        Dict[str, Any]
            A dictionary of available user attributes and their properties.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> attributes = schema_manager.user_attributes()
        >>> print(attributes)
        {'guac-email-address': {'type': 'STRING'}, 'guac-full-name': {'type': 'STRING'}, ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/userAttributes",
        )
        return result
