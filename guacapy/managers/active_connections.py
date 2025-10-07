import logging

import requests

from utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class ActiveConnectionManager:
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
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/activeConnections"

    def list(self):
        result = requester(
            method="GET",
            url=self.url,
            token=self.client.token,
            verify=self.client.verify,
        )
