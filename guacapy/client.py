#!/usr/bin/env python
# coding: utf-8

import logging
import requests
from utilities import (
    get_totp_token,
    set_log_level,
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

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("app.log")],
)


class GuacamoleError(Exception):
    """Custom exception for Guacamole API errors."""

    pass


class Guacamole:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        secret: str = None,
        connection_protocol: str = "https",
        connection_port: int = 443,
        base_url_path: str = "/",
        default_datasource: str = None,
        use_cookies: bool = False,
        ssl_verify: bool = True,
        logging_level: str = "INFO",
    ):
        set_log_level(logging_level)

        if connection_protocol != "https":
            connection_protocol = "http"
        self.method = connection_protocol

        self.base_url = f"{connection_protocol}://{hostname}:{connection_port}{base_url_path}api"
        self.username = username
        self.password = password
        self.secret = secret

        self.verify = ssl_verify
        if not self.verify:
            # Disable insecurity warnings if no verifying SSL certs.
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        resp = self._authenticate()
        auth = resp.json()
        assert "authToken" in auth, "Failed to retrieve auth token"
        assert "dataSource" in auth, "Failed to retrieve primary data source"
        assert "availableDataSources" in auth, "Failed to retrieve data sources"

        self.data_sources = auth["availableDataSources"]
        if default_datasource:
            assert (
                default_datasource in self.data_sources
            ), f"Datasource {default_datasource} does not exist. Possible values: {self.data_sources}"
            self.primary_datasource = default_datasource
        else:
            self.primary_datasource = auth["dataSource"]

        if use_cookies:
            self.cookies = resp.cookies
        else:
            self.cookies = None

        self.token = auth["authToken"]

    def _authenticate(self) -> requests.Response:
        parameters = {
            "username": self.username,
            "password": self.password,
        }
        if self.secret is not None:
            parameters["guac-totp"] = get_totp_token(self.secret)

        response = requests.post(
            url=f"{self.base_url}/tokens",
            data=parameters,
            verify=self.verify,
            allow_redirects=True,
        )
        response.raise_for_status()

        return response

    def _get_token(
        self,
        payload,
    ) -> str:
        """
        Submit a signed/encrypted payload (JSON) for the guacamole-auth-json extension
        Return a valid token
        """
        json_token = requester(
            method="POST",
            url=f"{self.base_url}/tokens",
            payload={"data": payload},
            verify=self.verify,
        )
        return json_token["authToken"]

    @property
    def active_connections(self) -> ActiveConnectionManager:
        return ActiveConnectionManager(self)

    @property
    def connection_groups(self) -> ConnectionGroupManager:
        return ConnectionGroupManager(self)

    @property
    def connections(self) -> ConnectionManager:
        return ConnectionManager(self)

    @property
    def sharing_profiles(self) -> SharingProfileManager:
        return SharingProfileManager(self)

    @property
    def user_groups(self) -> UserGroupManager:
        return UserGroupManager(self)

    @property
    def users(self) -> UserManager:
        return UserManager(self)
