import logging

import requests

from utilities import requester

# Get the logger for this module
logger = logging.getLogger(__name__)


class SharingProfileManager:
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
        self.url = f"{self.client.base_url}/session/data/{self.datasource}/sharingProfiles"


# def get_sharing_profile_parameters(
#     self,
#     sharing_profile_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/sharingProfiles/{sharing_profile_id}/parameters",
#     )
#
#
# def get_sharing_profile_full(
#     self,
#     sharing_profile_id,
#     datasource=None,
# ):
#     s = self.get_sharing_profile(
#         sharing_profile_id,
#         datasource,
#     )
#     s["parameters"] = self.get_sharing_profile_parameters(
#         sharing_profile_id,
#         datasource,
#     )
#     return s
#
#
# def get_sharing_profile(
#     self,
#     sharing_profile_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="GET",
#         url=f"{self.base_url}/session/data/{datasource}/sharingProfiles/{sharing_profile_id}",
#     )
#
#
# def add_sharing_profile(
#     self,
#     payload,
#     datasource=None,
# ):
#     """
#     Add/enable a sharing profile
#
#     Example payload:
#     {"primaryConnectionIdentifier":"8",
#     "name":"share",
#     "parameters":{"read-only":""},
#     "attributes":{}}'
#     """
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="POST",
#         url=f"{self.base_url}/session/data/{datasource}/sharingProfiles",
#         payload=payload,
#     )
#
#
# def delete_sharing_profile(
#     self,
#     sharing_profile_id,
#     datasource=None,
# ):
#     if not datasource:
#         datasource = self.primary_datasource
#     return self._request(
#         method="DELETE",
#         url=f"{self.base_url}/session/data/{datasource}/sharingProfiles/{sharing_profile_id}",
#         json_response=False,
#     )
