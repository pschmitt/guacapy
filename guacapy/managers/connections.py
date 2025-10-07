import logging

import requests

from utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class ConnectionManager:
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
            f"{self.client.base_url}/session/data/{self.datasource}/connections"
        )


# def get_connection(
#     self,
#     connection_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/connections/{connection_id}",
#     )
#
#
# def get_connection_parameters(
#     self,
#     connection_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/connections/{connection_id}/parameters",
#     )
#
#
# def get_connection_full(
#     self,
#     connection_id,
#     datasource=None,
# ):
#     c = self.get_connection(connection_id, datasource)
#     c["parameters"] = self.get_connection_parameters(
#         connection_id,
#         datasource,
#     )
#     return c
#
#
# def get_connection_by_name(
#     self,
#     name,
#     regex=False,
#     datasource=None,
# ):
#     """
#     Get a connection by its name
#     """
#     cons = self.get_connections(datasource)
#     res = self._get_connection_by_name(
#         cons,
#         name,
#         regex,
#     )
#     if not res:
#         logger.error(f"Could not find connection named {name}")
#     return res
#
#
# def add_connection(
#     self,
#     payload,
#     datasource=None,
# ):
#     """
#     Add a new connection
#
#     Example payload:
#     {"name":"iaas-067-mgt01 (Admin)",
#     "parentIdentifier":"4",
#     "protocol":"rdp",
#     "attributes":{"max-connections":"","max-connections-per-user":""},
#     "activeConnections":0,
#     "parameters":{
#         "port":"3389",
#         "enable-menu-animations":"true",
#         "enable-desktop-composition":"true",
#         "hostname":"iaas-067-mgt01.vcloud",
#         "color-depth":"32",
#         "enable-font-smoothing":"true",
#         "ignore-cert":"true",
#         "enable-drive":"true",
#         "enable-full-window-drag":"true",
#         "security":"any",
#         "password":"XXX",
#         "enable-wallpaper":"true",
#         "create-drive-path":"true",
#         "enable-theming":"true",
#         "username":"Administrator",
#         "console":"true",
#         "disable-audio":"true",
#         "domain":"iaas-067-mgt01.vcloud",
#         "drive-path":"/var/tmp",
#         "disable-auth":"",
#         "server-layout":"",
#         "width":"",
#         "height":"",
#         "dpi":"",
#         "console-audio":"",
#         "enable-printing":"",
#         "preconnection-id":"",
#         "enable-sftp":"",
#         "sftp-port":""}}
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="POST",
#         url=f"{self.base_url}/session/data/{datasource}/connections",
#         payload=payload,
#     )
#
#
# def edit_connection(
#     self,
#     connection_id,
#     payload,
#     datasource=None,
# ):
#     """
#     Edit an existing connection
#
#     Example payload:
#     {"name":"test",
#     "identifier":"7",
#     "parentIdentifier":"ROOT",
#     "protocol":"rdp",
#     "attributes":{"max-connections":"","max-connections-per-user":""},
#     "activeConnections":0,
#     "parameters":{
#         "disable-audio":"true",
#         "server-layout":"fr-fr-azerty",
#         "domain":"dt",
#         "hostname":"127.0.0.1",
#         "enable-font-smoothing":"true",
#         "security":"rdp",
#         "port":"3389",
#         "disable-auth":"",
#         "ignore-cert":"",
#         "console":"",
#         "width":"",
#         "height":"",
#         "dpi":"",
#         "color-depth":"",
#         "console-audio":"",
#         "enable-printing":"",
#         "enable-drive":"",
#         "create-drive-path":"",
#         "enable-wallpaper":"",
#         "enable-theming":"",
#         "enable-full-window-drag":"",
#         "enable-desktop-composition":"",
#         "enable-menu-animations":"",
#         "preconnection-id":"",
#         "enable-sftp":"",
#         "sftp-port":""}}
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="PUT",
#         url=f"{self.base_url}/session/data/{datasource}/connections/{connection_id}",
#         payload=payload,
#         json_response=False,
#     )
#
#
# def delete_connection(
#     self,
#     connection_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="DELETE",
#         url=f"{self.base_url}/session/data/{datasource}/connections/{connection_id}",
#         json_response=False,
#     )
