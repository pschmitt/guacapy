import logging

import requests

from utilities import requester

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

    def list(self):
        result = requester(
            method="GET",
            url=self.url,
            token=self.client.token,
            verify=self.client.verify,
        )
        return result

    def get(
        self,
        username: str,
    ) -> requests.Response:
        result = requester(
            method="GET",
            url=f"{self.url}/{username}",
            token=self.client.token,
            verify=self.client.verify,
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
            method="POST",
            url=self.url,
            payload=payload,
            token=self.client.token,
            verify=self.client.verify,
        )
        return result

    def update(
        self,
        username: str,
        payload: dict,
    ) -> None:
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
        return requester(
            method="PUT",
            url=f"{self.url}/{username}",
            payload=payload,
            json_response=False,
            token=self.client.token,
            verify=self.client.verify,
        )

    def delete(
        self,
        username: str,
    ) -> None:
        return requester(
            method="DELETE",
            url=f"{self.url}/{username}",
            json_response=False,
            token=self.client.token,
            verify=self.client.verify,
        )

    def get_permissions(
        self,
        username: str,
    ) -> dict:
        result = requester(
            method="GET",
            url=f"{self.url}/{username}/permissions",
            token=self.client.token,
            verify=self.client.verify,
        )
        return result

    def get_usergroups(
        self,
        username,
    ):
        """
        List the usergroups a user belongs to
        """
        result = requester(
            method="GET",
            url=f"{self.url}/{username}/userGroups",
            token=self.client.token,
            verify=self.client.verify,
        )
        return result

    def grant_permission(
        self,
        username,
        payload,
    ):
        """
        Example payload:
        [{"op":"add","path":"/systemPermissions","value":"ADMINISTER"}]
        """
        result = requester(
            method="PATCH",
            url=f"{self.url}/{username}/permissions",
            payload=payload,
            json_response=False,
            token=self.client.token,
            verify=self.client.verify,
        )
        return result

    def revoke_permissions(
        self,
        username: str,
        permissions: dict,
    ) -> None:
        # FIXME: I don't know if this API endpoint even exists.
        asdf = (
            self.client.token
        )  # Junk to remove static method warning for now.

        """Remove permissions from a user."""
        logging.warning("Method not yet implemented.")
