#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals
from __future__ import print_function
from simplejson.scanner import JSONDecodeError
import logging
import re
import requests


import hmac
import base64
import struct
import hashlib
import time

logger = logging.getLogger(__name__)


def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = bytes(hmac.new(key, msg, hashlib.sha1).digest())
    o = h[19] & 15
    h = (struct.unpack(">I", h[o : o + 4])[0] & 0x7FFFFFFF) % 1000000
    return h


def get_totp_token(secret):
    return get_hotp_token(secret, intervals_no=int(time.time()) // 30)


class Guacamole:
    def __init__(
        self,
        hostname,
        username,
        password,
        secret=None,
        method="https",
        url_path="/",
        default_datasource=None,
        verify=True,
    ):
        if method.lower() not in ["https", "http"]:
            raise ValueError("Only http and https methods are valid.")
        self.REST_API = "{}://{}{}/api".format(method, hostname, url_path)
        self.username = username
        self.password = password
        self.secret = secret
        self.verify = verify
        auth = self.__authenticate()
        assert "authToken" in auth, "Failed to retrieve auth token"
        assert "dataSource" in auth, "Failed to retrieve primaray data source"
        assert "availableDataSources" in auth, "Failed to retrieve data sources"
        self.datasources = auth["availableDataSources"]
        if default_datasource:
            assert (
                default_datasource in self.datasources
            ), "Datasource {} does not exist. Possible values: {}".format(
                default_datasource, self.datasources
            )
            self.primary_datasource = default_datasource
        else:
            self.primary_datasource = auth["dataSource"]
        self.token = auth["authToken"]

    def __authenticate(self):
        parameters = {"username": self.username, "password": self.password}
        if self.secret is not None:
            parameters["guac-totp"] = get_totp_token(self.secret)
        r = requests.post(
            url=self.REST_API + "/tokens",
            data=parameters,
            verify=self.verify,
            allow_redirects=True,
        )
        r.raise_for_status()
        return r.json()

    def __auth_request(
        self, method, url, payload=None, url_params=None, json_response=True
    ):
        params = [("token", self.token)]
        if url_params:
            params += url_params
        logger.debug(
            "{method} {url} - Params: {params}- Payload: {payload}".format(
                method=method, url=url, params=params, payload=payload
            )
        )
        r = requests.request(
            method=method,
            url=url,
            params=params,
            json=payload,
            verify=self.verify,
            allow_redirects=True,
        )
        if not r.ok:
            logger.error(r.content)
        r.raise_for_status()
        if json_response:
            try:
                return r.json()
            except JSONDecodeError:
                logger.error("Could not decode JSON response")
                return r
        else:
            return r

    def get_connections(self, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        params = [
            ("permission", "UPDATE"),
            ("permission", "DELETE"),
        ]
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/connectionGroups/ROOT/tree".format(
                self.REST_API, datasource
            ),
            url_params=params,
        )

    def get_active_connections(self, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/activeConnections".format(
                self.REST_API, datasource
            ),
        )

    def get_connection(self, connection_id, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/connections/{}".format(
                self.REST_API, datasource, connection_id
            ),
        )

    def get_connection_parameters(self, connection_id, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/connections/{}/parameters".format(
                self.REST_API, datasource, connection_id
            ),
        )

    def get_connection_full(self, connection_id, datasource=None):
        c = self.get_connection(connection_id, datasource)
        c["parameters"] = self.get_connection_parameters(
            connection_id, datasource
        )
        return c

    def __get_connection_by_name(self, cons, name, regex=False):
        # FIXME This need refactoring (DRY)
        if "childConnections" not in cons:
            if "childConnectionGroups" in cons:
                for c in cons["childConnectionGroups"]:
                    res = self.__get_connection_by_name(c, name, regex)
                    if res:
                        return res
        else:
            children = cons["childConnections"]
            if regex:
                res = [x for x in children if re.search(name, x["name"])]
            else:
                res = [x for x in children if x["name"] == name]
            if not res:
                if "childConnectionGroups" in cons:
                    for c in cons["childConnectionGroups"]:
                        res = self.__get_connection_by_name(c, name, regex)
                        if res:
                            return res
            else:
                return res[0]

    def get_connection_by_name(self, name, regex=False, datasource=None):
        """
        Get a connection group by its name
        """
        cons = self.get_connections(datasource)
        res = self.__get_connection_by_name(cons, name, regex)
        if not res:
            logger.error("Could not find connection named {}".format(name))
        return res

    def add_connection(self, payload, datasource=None):
        """
        Add a new connection

        Example payload:
        {"name":"iaas-067-mgt01 (Admin)",
        "parentIdentifier":"4",
        "protocol":"rdp",
        "attributes":{"max-connections":"","max-connections-per-user":""},
        "activeConnections":0,
        "parameters":{
            "port":"3389",
            "enable-menu-animations":"true",
            "enable-desktop-composition":"true",
            "hostname":"iaas-067-mgt01.vcloud",
            "color-depth":"32",
            "enable-font-smoothing":"true",
            "ignore-cert":"true",
            "enable-drive":"true",
            "enable-full-window-drag":"true",
            "security":"any",
            "password":"XXX",
            "enable-wallpaper":"true",
            "create-drive-path":"true",
            "enable-theming":"true",
            "username":"Administrator",
            "console":"true",
            "disable-audio":"true",
            "domain":"iaas-067-mgt01.vcloud",
            "drive-path":"/var/tmp",
            "disable-auth":"",
            "server-layout":"",
            "width":"",
            "height":"",
            "dpi":"",
            "console-audio":"",
            "enable-printing":"",
            "preconnection-id":"",
            "enable-sftp":"",
            "sftp-port":""}}
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="POST",
            url="{}/session/data/{}/connections".format(
                self.REST_API, datasource
            ),
            payload=payload,
        )

    def edit_connection(self, connection_id, payload, datasource=None):
        """
        Edit an existing connection

        Example payload:
        {"name":"test",
        "identifier":"7",
        "parentIdentifier":"ROOT",
        "protocol":"rdp",
        "attributes":{"max-connections":"","max-connections-per-user":""},
        "activeConnections":0,
        "parameters":{
            "disable-audio":"true",
            "server-layout":"fr-fr-azerty",
            "domain":"dt",
            "hostname":"127.0.0.1",
            "enable-font-smoothing":"true",
            "security":"rdp",
            "port":"3389",
            "disable-auth":"",
            "ignore-cert":"",
            "console":"",
            "width":"",
            "height":"",
            "dpi":"",
            "color-depth":"",
            "console-audio":"",
            "enable-printing":"",
            "enable-drive":"",
            "create-drive-path":"",
            "enable-wallpaper":"",
            "enable-theming":"",
            "enable-full-window-drag":"",
            "enable-desktop-composition":"",
            "enable-menu-animations":"",
            "preconnection-id":"",
            "enable-sftp":"",
            "sftp-port":""}}
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="PUT",
            url="{}/session/data/{}/connections/{}".format(
                self.REST_API, datasource, connection_id
            ),
            payload=payload,
            json_response=False,
        )

    def delete_connection(self, connection_id, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="DELETE",
            url="{}/session/data/{}/connections/{}".format(
                self.REST_API, datasource, connection_id
            ),
            json_response=False,
        )

    def get_history(self, datasource=None):
        if not datasource:
            datasource = self.primary_datasource

        raise NotImplementedError()

    def __get_connection_group_by_name(self, cons, name, regex=False):
        if (regex and re.search(name, cons["name"])) or (
            not regex and cons["name"] == name
        ):
            return cons
        if "childConnectionGroups" in cons:
            children = cons["childConnectionGroups"]
            if regex:
                res = [x for x in children if re.search(name, x["name"])]
            else:
                res = [x for x in children if x["name"] == name]
            if res:
                return res[0]
            for c in cons["childConnectionGroups"]:
                res = self.__get_connection_group_by_name(c, name, regex)
                if res:
                    return res

    def get_connection_group_by_name(self, name, regex=False, datasource=None):
        """
        Get a connection group by its name
        """
        if not datasource:
            datasource = self.primary_datasource
        cons = self.get_connections(datasource)
        return self.__get_connection_group_by_name(cons, name, regex)

    def get_connection_group(self, connectiongroup_id, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/connectionGroups/{}".format(
                self.REST_API, datasource, connectiongroup_id
            ),
        )

    def add_connection_group(self, payload, datasource=None):
        """
        Create a new connection group

        Example payload:
        {"parentIdentifier":"ROOT",
        "name":"iaas-099 (Test)",
        "type":"ORGANIZATIONAL",
        "attributes":{"max-connections":"","max-connections-per-user":""}}
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="POST",
            url="{}/session/data/{}/connectionGroups".format(
                self.REST_API, datasource
            ),
            payload=payload,
        )

    def edit_connection_group(
        self, connection_group_id, payload, datasource=None
    ):
        """
        Edit an exiting connection group

        Example payload:
        {"parentIdentifier":"ROOT",
        "name":"iaas-099 (Test)",
        "type":"ORGANIZATIONAL",
        "attributes":{"max-connections":"","max-connections-per-user":""}}
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="PUT",
            url="{}/session/data/{}/connectionGroups/{}".format(
                self.REST_API, datasource, connection_group_id,
            ),
            payload=payload,
        )

    def delete_connection_group(self, connection_group_id, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="DELETE",
            url="{}/session/data/{}/connectionGroups/{}".format(
                self.REST_API, datasource, connection_group_id
            ),
        )

    def get_users(self, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/users".format(self.REST_API, datasource,),
        )

    def add_user(self, payload, datasource=None):
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
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="POST",
            url="{}/session/data/{}/users".format(self.REST_API, datasource),
            payload=payload,
        )

    def edit_user(self, username, payload, datasource=None):
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
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="PUT",
            url="{}/session/data/{}/users/{}".format(
                self.REST_API, datasource, username
            ),
            payload=payload,
            json_response=False,
        )

    def get_user(self, username, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/users/{}".format(
                self.REST_API, datasource, username
            ),
        )

    def delete_user(self, username, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="DELETE",
            url="{}/session/data/{}/users/{}".format(
                self.REST_API, datasource, username
            ),
        )

    def get_permissions(self, username, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/users/{}/permissions".format(
                self.REST_API, datasource, username
            ),
        )

    def grant_permission(self, username, payload, datasource=None):
        """
        Example payload:
        [{"op":"add","path":"/systemPermissions","value":"ADMINISTER"}]
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="PATCH",
            url="{}/session/data/{}/users/{}/permissions".format(
                self.REST_API, datasource, username
            ),
            payload=payload,
            json_response=False,
        )

    def get_sharing_profile(self, sharing_profile_id, datasource=None):
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/sharingProfiles/{}".format(
                self.REST_API, datasource, sharing_profile_id
            ),
        )

    def add_sharing_profile(self, payload, datasource=None):
        """
        Add/enable a sharing profile

        Example payload:
        {"primaryConnectionIdentifier":"8",
        "name":"share",
        "parameters":{"read-only":""},
        "attributes":{}}'
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="POST",
            url="{}/session/data/{}/sharingProfiles".format(
                self.REST_API, datasource
            ),
            payload=payload,
        )

    def get_user_groups(self, datasource=None):
        """
        List User Groups
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/userGroups".format(
                self.REST_API, datasource,
            ),
        )

    def get_group(self, usergroup, datasource=None):
        """
        Details of User Group
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="GET",
            url="{}/session/data/{}/userGroups/{}".format(
                self.REST_API, datasource, usergroup
            ),
        )

    def edit_group_members(self, usergroup, payload, datasource=None):
        """
        Add Members to User Group
        Example add payload:
        [{"op":"add","path":"/","value":"username"}]
        Example remove payload:
        [{"op":"remove","path":"/","value":"username"}]
        """
        if not datasource:
            datasource = self.primary_datasource
        return self.__auth_request(
            method="PATCH",
            url="{}/session/data/{}/userGroups/{}/memberUsers".format(
                self.REST_API, datasource, usergroup
            ),
            payload=payload,
            json_response=False,
        )
