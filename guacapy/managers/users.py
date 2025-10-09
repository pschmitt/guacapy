import logging
import requests
from utilities import requester
from typing import Dict, List, Any

# Get the logger for this module
logger = logging.getLogger(__name__)


class UserManager:
    def __init__(
        self,
        client,
        datasource=None,
    ):
        self.client = client
        if datasource:
            self.datasource = datasource
        else:
            self.datasource = self.client.primary_datasource
        self.url = (
            f"{self.client.base_url}/session/data/{self.datasource}/users"
        )

    def list(self) -> dict:
        result = requester(
            client=self.client,
            url=self.url,
        )
        return result

    def get(
        self,
        username: str,
    ) -> requests.Response:
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}",
        )
        return result

    def create(
        self,
        payload: dict,
    ) -> requests.Response:
        """
        Add/enable a user

        Example payload:
        {"username":"test"
         "password":"testpwd",
         "attributes":{
                "disabled":"",
                "expired":"",
                "access-window-start":"",
                "access-window-end":"",
                "valid-from":"",
                "valid-until":"",
                "timezone":null}}
        """
        result = requester(
            client=self.client,
            url=self.url,
            method="POST",
            payload=payload,
        )
        return result

    def update(
        self,
        username: str,
        payload: dict,
    ) -> requests.Response:
        """
        Edit a user

        Example payload:
        {
            "username": "username",
            "attributes": {
                "guac-email-address": null,
                "guac-organizational-role": null,
                "guac-full-name": null,
                "expired": "",
                "timezone": null,
                "access-window-start": "",
                "guac-organization": null,
                "access-window-end": "",
                "disabled": "",
                "valid-until": "",
                "valid-from": ""
            },
            "lastActive": 1588030687251,
            "password": "password"
        }
        """
        result = requester(
            client=self.client,
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
        return requester(
            client=self.client,
            url=f"{self.url}/{username}",
            method="DELETE",
            json_response=False,
        )

    def get_permissions(
        self,
        username: str,
    ) -> requests.Response:
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/permissions",
        )
        return result

    def get_usergroups(
        self,
        username,
    ) -> requests.Response:
        """
        List the usergroups a user belongs to
        """
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/userGroups",
        )
        return result

    def grant_permission(
        self,
        username,
        payload,
    ) -> requests.Response:
        """
        Example payload:
        [{"op":"add","path":"/systemPermissions","value":"ADMINISTER"}]
        """
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/permissions",
            method="PATCH",
            payload=payload,
            json_response=False,
        )
        return result

    def revoke_permissions(
        self,
        username: str,
        permissions: dict,
    ) -> requests.Response:
        # TODO: I don't know if this API endpoint even exists.
        asdf = (
            self.client.token
        )  # Junk to remove static method warning for now.

        """Remove permissions from a user."""
        logging.warning("Method not yet implemented.")
        result = requester(
            client=self.client,
            url=f"{self.url}/{username}/permissions",
        )
        return result
