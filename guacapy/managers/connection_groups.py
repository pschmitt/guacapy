import logging

import requests

from utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class ConnectionGroupManager:
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
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/connectionGroups"


# def get_connections(
#     self,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     params = [
#         ("permission", "UPDATE"),
#         ("permission", "DELETE"),
#     ]
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/connectionGroups/ROOT/tree",
#         params=params,
#     )
#
#
# def get_connection_group_connections(
#     self,
#     connection_group_id,
#     datasource=None,
# ):
#     """Get a list of connections linked to an organizational or balancing
#     connection group"""
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/connectionGroups/{connection_group_id}/tree",
#     )
#
#
# def get_connection_group(
#     self,
#     connectiongroup_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/connectionGroups/{connectiongroup_id}",
#     )
#
#
# def add_connection_group(
#     self,
#     payload,
#     datasource=None,
# ):
#     """
#     Create a new connection group
#
#     Example payload:
#     {"parentIdentifier":"ROOT",
#     "name":"iaas-099 (Test)",
#     "type":"ORGANIZATIONAL",
#     "attributes":{"max-connections":"","max-connections-per-user":""}}
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="POST",
#         url=f"{self.base_url}/session/data/{datasource}/connectionGroups",
#         payload=payload,
#     )
#
#
# def edit_connection_group(
#     self,
#     connection_group_id,
#     payload,
#     datasource=None,
# ):
#     """
#     Edit an exiting connection group
#
#     Example payload:
#     {"parentIdentifier":"ROOT",
#     "name":"iaas-099 (Test)",
#     "type":"ORGANIZATIONAL",
#     "attributes":{"max-connections":"","max-connections-per-user":""}}
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="PUT",
#         url=f"{self.base_url}/session/data/{datasource}/connectionGroups/{connection_group_id}",
#         payload=payload,
#         json_response=False,
#     )
#
#
# def delete_connection_group(
#     self,
#     connection_group_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="DELETE",
#         url=f"{self.base_url}/session/data/{datasource}/connectionGroups/{connection_group_id}",
#         json_response=False,
#     )
