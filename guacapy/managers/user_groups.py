import logging

import requests

from utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class UserGroupManager:
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
            f"{self.client.base_url}/session/data/{self.datasource}/userGroups"
        )


# def get_user_groups(
#     self,
#     datasource=None,
# ):
#     """
#     List all user groups
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups",
#     )
#
#
# def add_group(
#     self,
#     payload,
#     datasource=None,
# ):
#     """
#     Add/enable a user group
#
#     Example payload:
#     {"identifier":"test"
#      "attributes":{
#             "disabled":""}}
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="POST",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups",
#         payload=payload,
#     )
#
#
# def delete_group(
#     self,
#     usergroup,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="DELETE",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups/{usergroup}",
#         json_response=False,
#     )
#
#
# def get_group(
#     self,
#     usergroup,
#     datasource=None,
# ):
#     """
#     Details of User Group
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups/{usergroup}",
#     )
#
#
# def get_group_members(
#     self,
#     usergroup,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups/{usergroup}/memberUsers",
#     )
#
#
# def edit_group_members(
#     self,
#     usergroup,
#     payload,
#     datasource=None,
# ):
#     """
#     Add Members to User Group
#     Example add payload:
#     [{"op":"add","path":"/","value":"username"}]
#     Example remove payload:
#     [{"op":"remove","path":"/","value":"username"}]
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="PATCH",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups/{usergroup}/memberUsers",
#         payload=payload,
#         json_response=False,
#     )
#
#
# def grant_group_permission(
#     self,
#     groupname,
#     payload,
#     datasource=None,
# ):
#     """
#     Example payload:
#     [{"op":"add","path":"/systemPermissions","value":"ADMINISTER"}]
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="PATCH",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups/{groupname}/permissions",
#         payload=payload,
#         json_response=False,
#     )
#
#
# def get_group_permissions(
#     self,
#     groupname,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/userGroups/{groupname}/permissions",
#     )
