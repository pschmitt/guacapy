"""
Base manager class for Guacamole API managers.
"""

from typing import Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseManager:
    """
    Base class for Guacamole API managers, handling common initialization logic.

    Attributes
    ----------
    client : Any
        The Guacamole client instance with authentication details.
    datasource : str
        The data source identifier (e.g., 'mysql', 'postgresql').
    """

    def __init__(
        self,
        client: Any,
        datasource: Optional[str] = None,
    ):
        """
        Initialize the manager with a Guacamole client and data source.

        Parameters
        ----------
        client : Any
            The Guacamole client instance with base_url and authentication details.
        datasource : Optional[str], optional
            The data source identifier. Defaults to client.primary_datasource if None.

        Raises
        ------
        requests.HTTPError
            If the API authentication fails or the datasource is invalid.
        """
        self.client = client
        self.datasource = datasource or client.primary_datasource
