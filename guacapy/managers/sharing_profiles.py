"""
Sharing profile management module for the Guacamole REST API.

This module provides the `SharingProfileManager` class to interact with sharing profile endpoints
of the Apache Guacamole REST API, enabling operations such as listing sharing profiles, retrieving
profile details, creating, updating, and deleting sharing profiles.

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
Create a client and list sharing profiles:
>>> from guacapy import Guacamole
>>> client = Guacamole(
...     hostname="guacamole.example.com",
...     username="admin",
...     password="secret",
...     datasource="mysql"
... )
>>> profile_manager = client.sharing_profiles
>>> profiles = profile_manager.list()
>>> print(profiles)
{'1': {'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}}
"""

import logging
import requests
from typing import Dict, Any, Optional
from .base import BaseManager
from ..utilities import requester, validate_payload

# Get the logger for this module
logger = logging.getLogger(__name__)


class SharingProfileManager(BaseManager):
    PROFILE_TEMPLATE: Dict[str, Any] = {
        "name": "",
        "primaryConnectionIdentifier": "",
        "parameters": {"read-only": ""},
        "attributes": {},
    }

    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the SharingProfileManager for interacting with Guacamole sharing profile endpoints.

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
            The base URL for sharing profile endpoints.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        super().__init__(client, datasource)
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/sharingProfiles"

    def list(self) -> Dict[str, Any]:
        """
        Retrieve a list of all sharing profiles in the datasource.

        Returns
        -------
        Dict[str, Any]
            A dictionary mapping sharing profile identifiers to their details.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 401 for unauthorized, 403 for insufficient permissions).

        Examples
        --------
        >>> profiles = profile_manager.list()
        >>> print(profiles)
        {'1': {'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}}
        """
        result = requester(
            guac_client=self.client,
            url=self.url,
        )
        return result

    def details(
        self,
        identifier: str,
    ) -> Dict[str, Any]:
        """
        Retrieve details for a specific sharing profile.

        Parameters
        ----------
        identifier : str
            The identifier of the sharing profile to retrieve details for.

        Returns
        -------
        Dict[str, Any]
            The sharing profile details, including name and primary connection identifier.

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent profile, 401 for unauthorized).

        Examples
        --------
        >>> profile = profile_manager.details("1")
        >>> print(profile)
        {'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
        )
        return result

    def parameters(
        self,
        identifier: str,
    ) -> Dict[str, Any]:
        """
        Retrieve parameters for a specific sharing profile.

        Parameters
        ----------
        identifier : str
            The identifier of the sharing profile to retrieve parameters for.

        Returns
        -------
        Dict[str, Any]
            The sharing profile parameters (e.g., read-only settings).

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent profile, 401 for unauthorized).

        Examples
        --------
        >>> params = profile_manager.parameters("1")
        >>> print(params)
        {'read-only': '', ...}
        """
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}/parameters",
        )
        return result

    def create(
        self,
        payload: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new sharing profile.

        Parameters
        ----------
        payload : Dict[str, Any]
            The sharing profile creation payload. Must conform to PROFILE_TEMPLATE.

        Returns
        -------
        Optional[Dict[str, Any]]
            The created sharing profile details, or None if the profile already exists (400 error).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails for reasons other than 400.

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(SharingProfileManager.PROFILE_TEMPLATE)
        >>> payload.update({
        ...     "name": "testprofile",
        ...     "primaryConnectionIdentifier": "1"
        ... })
        >>> profile = profile_manager.create(payload)
        """
        validate_payload(payload, self.PROFILE_TEMPLATE)
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
                    f"Failed to create sharing profile {payload.get('name')} (already exists, 400)"
                )
                return None
            raise

    def update(
        self,
        identifier: str,
        payload: Dict[str, Any],
    ) -> requests.Response:
        """
        Update an existing sharing profile.

        Parameters
        ----------
        identifier : str
            The identifier of the sharing profile to update.
        payload : Dict[str, Any]
            The update payload. Must conform to PROFILE_TEMPLATE.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        ValueError
            If the payload is invalid.
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent profile, 400 for invalid payload).

        Examples
        --------
        >>> from copy import deepcopy
        >>> payload = deepcopy(SharingProfileManager.PROFILE_TEMPLATE)
        >>> payload.update({
        ...     "identifier": "2",
        ...     "name": "testprofile_updated",
        ...     "primaryConnectionIdentifier": "1"
        ... })
        >>> response = profile_manager.update("2", payload)
        """
        validate_payload(payload, self.PROFILE_TEMPLATE)
        result = requester(
            guac_client=self.client,
            url=f"{self.url}/{identifier}",
            method="PUT",
            payload=payload,
            json_response=False,
        )
        return result

    def delete(
        self,
        identifier: str,
    ) -> requests.Response:
        """
        Delete a sharing profile.

        Parameters
        ----------
        identifier : str
            The identifier of the sharing profile to delete.

        Returns
        -------
        requests.Response
            The HTTP response indicating success (204 No Content).

        Raises
        ------
        requests.HTTPError
            If the API request fails (e.g., 404 for non-existent profile, 401 for unauthorized).

        Examples
        --------
        >>> response = profile_manager.delete("2")
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
