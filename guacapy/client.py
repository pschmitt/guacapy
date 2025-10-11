#!/usr/bin/env python
# coding: utf-8

"""
Guacamole API client module.

This module provides the `Guacamole` class for authenticating with and interacting with the
Guacamole REST API, along with manager classes for handling resources like users, connections,
and groups.

Examples
--------
>>> from guacapy import Guacamole
>>> client = Guacamole(
...     hostname="guacamole.example.com",
...     username="admin",
...     password="secret",
...     datasource="mysql"
... )
>>> users = client.users.list()
"""

import logging
import requests
import urllib3
from typing import Any, Dict, Optional
from utilities import (
    get_totp_token,
    configure_logging,
    requester,
)
from .managers import (
    ActiveConnectionManager,
    ConnectionGroupManager,
    ConnectionManager,
    SharingProfileManager,
    UserGroupManager,
    UserManager,
)

# Get the logger for this module
logger = logging.getLogger(__name__)


class GuacamoleError(Exception):
    """
    Custom exception for Guacamole API errors.

    Parameters
    ----------
    message : str
        The error message describing the issue.
    """

    pass


class Guacamole:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        secret: Optional[str] = None,
        connection_protocol: str = "https",
        connection_port: int = 443,
        base_url_path: str = "/",
        default_datasource: Optional[str] = None,
        use_cookies: bool = False,
        ssl_verify: bool = False,
        logging_level: Optional[str] = None,
    ):
        """
        Initialize the Guacamole client for interacting with the Guacamole REST API.

        Parameters
        ----------
        hostname : str
            The hostname of the Guacamole server (e.g., "guacamole.example.com").
        username : str
            The username for authentication.
        password : str
            The password for authentication.
        secret : Optional[str], optional
            The TOTP secret for two-factor authentication, if required. Defaults to None.
        connection_protocol : str, optional
            The protocol for the API connection ("http" or "https"). Defaults to "https".
        connection_port : int, optional
            The port for the API connection. Defaults to 443.
        base_url_path : str, optional
            The base path for the API (e.g., "/"). Defaults to "/".
        default_datasource : Optional[str], optional
            The default data source identifier. Defaults to the primary data source from authentication.
        use_cookies : bool, optional
            Whether to use cookies for authentication. Defaults to False.
        ssl_verify : bool, optional
            Whether to verify SSL certificates. Defaults to False.
        logging_level : Optional[str], optional
            The logging level (e.g., "DEBUG", "INFO"). Defaults to None (no logging configuration).

        Raises
        ------
        GuacamoleError
            If authentication fails or the specified data source is invalid.
        """
        if logging_level is not None:
            configure_logging(logging_level)

        if connection_protocol not in {"http", "https"}:
            raise GuacamoleError(
                f"Invalid connection protocol: {connection_protocol}. Must be 'http' or 'https'."
            )
        self.protocol = connection_protocol

        self.base_url = f"{connection_protocol}://{hostname}:{connection_port}{base_url_path}api"
        self.username = username
        self.password = password
        self.secret = secret

        self.verify = ssl_verify
        if not self.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = self._authenticate()
        auth_response = response.json()
        if not all(
            key in auth_response
            for key in ("authToken", "dataSource", "availableDataSources")
        ):
            raise GuacamoleError(
                "Authentication failed: Missing required fields in response"
            )

        self.data_sources = auth_response["availableDataSources"]
        if default_datasource:
            if default_datasource not in self.data_sources:
                raise GuacamoleError(
                    f"Datasource {default_datasource} does not exist. Possible values: {self.data_sources}"
                )
            self.primary_datasource = default_datasource
        else:
            self.primary_datasource = auth_response["dataSource"]

        self.cookies = response.cookies if use_cookies else None
        self.token = auth_response["authToken"]

    def _authenticate(self) -> requests.Response:
        """
        Authenticate with the Guacamole API to obtain an authentication token.

        Sends a POST request to /api/tokens with x-www-form-urlencoded data containing
        username, password, and optionally guac-totp for two-factor authentication.

        Returns
        -------
        requests.Response
            The HTTP response containing the authentication token and data source details (200 OK).

        Raises
        ------
        requests.HTTPError
            If the authentication request fails (e.g., 401 Unauthorized for invalid credentials).
        GuacamoleError
            If the response is missing required fields.
        """
        parameters = {
            "username": self.username,
            "password": self.password,
        }
        if self.secret is not None:
            parameters["guac-totp"] = get_totp_token(self.secret)

        try:
            response = requests.post(
                url=f"{self.base_url}/tokens",
                data=parameters,
                verify=self.verify,
                allow_redirects=True,
            )
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise GuacamoleError(
                    "Authentication failed: Invalid username or password"
                ) from e
            raise
        return response

    def get_json_token(
        self,
        payload: Dict[str, Any],
    ) -> str:
        """
        Submit a signed/encrypted payload for the guacamole-auth-json extension to obtain a token.

        This method supports the guacamole-auth-json extension, which is not part of the standard
        Guacamole API but allows JSON-based authentication.

        Parameters
        ----------
        payload : Dict[str, Any]
            The JSON payload to submit for authentication.

        Returns
        -------
        str
            The authentication token received from the API (200 OK).

        Examples
        --------
        >>> payload = {"data": {"username": "john_doe", "password": "secret"}}
        >>> token = client.get_json_token(payload)
        """
        json_token = requester(
            guac_client=self,
            method="POST",
            url=f"{self.base_url}/tokens",
            payload={"data": payload},
        )
        return json_token["authToken"]

    def logout(self) -> None:
        """
        Revoke the current authentication token, ending the session.

        Sends a DELETE request to /api/tokens/{token}, expecting a 204 No Content response.

        Returns
        -------
        None
            No return value (204 No Content).

        Raises
        ------
        requests.HTTPError
            If the logout request fails.
        """
        requester(
            guac_client=self,
            method="DELETE",
            url=f"{self.base_url}/tokens/{self.token}",
            json_response=False,
        )
        self.token = None  # Clear token to prevent reuse

    @property
    def active_connections(self) -> ActiveConnectionManager:
        """
        Get the manager for active connections.

        Returns
        -------
        ActiveConnectionManager
            The manager instance for handling active connections.
        """
        return ActiveConnectionManager(self)

    @property
    def connection_groups(self) -> ConnectionGroupManager:
        """
        Get the manager for connection groups.

        Returns
        -------
        ConnectionGroupManager
            The manager instance for handling connection groups.
        """
        return ConnectionGroupManager(self)

    @property
    def connections(self) -> ConnectionManager:
        """
        Get the manager for connections.

        Returns
        -------
        ConnectionManager
            The manager instance for handling connections.
        """
        return ConnectionManager(self)

    @property
    def sharing_profiles(self) -> SharingProfileManager:
        """
        Get the manager for sharing profiles.

        Returns
        -------
        SharingProfileManager
            The manager instance for handling sharing profiles.
        """
        return SharingProfileManager(self)

    @property
    def user_groups(self) -> UserGroupManager:
        """
        Get the manager for user groups.

        Returns
        -------
        UserGroupManager
            The manager instance for handling user groups.
        """
        return UserGroupManager(self)

    @property
    def users(self) -> UserManager:
        """
        Get the manager for users.

        Returns
        -------
        UserManager
            The manager instance for handling users.
        """
        return UserManager(self)
