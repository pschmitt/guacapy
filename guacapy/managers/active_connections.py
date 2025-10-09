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

    def list(self) -> requests.Response:
        result = requester(
            client=self.client,
            url=self.url,
        )
        return result
