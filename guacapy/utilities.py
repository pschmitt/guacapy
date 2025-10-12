"""
Utility functions for the Guacamole API client.

This module provides helper functions for authentication, logging, and resource querying
in the `guacapy` package, supporting the `Guacamole` client and its managers.

Examples
--------
>>> from guacapy import Guacamole
>>> client = Guacamole(
...     hostname="guacamole.example.com",
...     username="admin",
...     password="secret"
... )
>>> configure_logging("DEBUG")
>>> response = requester(client, url=f"{client.base_url}/session/data/mysql/users")
"""

import hmac
import base64
import struct
import hashlib
import time
import logging
import re
import requests
from json.decoder import JSONDecodeError
from typing import Union, Dict, List, Any, Optional

# Get the logger for this module
logger = logging.getLogger(__name__)

def configure_logging(
    level: Optional[str] = None,
    logger_name: str = "",
    log_file: Optional[str] = "app.log",
) -> None:
    """
    Configure logging for the application.

    Parameters
    ----------
    level : Optional[str], optional
        The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). Defaults to None (no configuration).
    logger_name : str, optional
        The name of the logger to configure. Defaults to the root logger.
    log_file : Optional[str], optional
        The file to write logs to. Defaults to "app.log". If None, only console logging is configured.

    Raises
    ------
    ValueError
        If the provided logging level is invalid.

    Examples
    --------
    >>> configure_logging(level="DEBUG", log_file="guacapy.log")
    """
    if level is None:
        return

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }
    level = level.upper()
    if level not in level_map:
        valid_levels = ", ".join(level_map.keys())
        raise ValueError(
            f"Invalid logging level '{level}'. Valid options are: {valid_levels}"
        )

    my_logger = logging.getLogger(logger_name)
    my_logger.setLevel(level_map[level])
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    my_logger.handlers = [stream_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        my_logger.handlers.append(file_handler)
    my_logger.log(
        level_map[level],
        f"Logging configured for '{logger_name or 'root'}' at level {level}",
    )

def requester(
    guac_client: Any,
    url: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    payload: Union[Dict[str, Any], List[Any], None] = None,
    token: Optional[str] = None,
    verify: Optional[bool] = None,
    allow_redirects: bool = True,
    cookies: Optional[Dict[str, Any]] = None,
    json_response: bool = True,
) -> Union[requests.Response, Dict[str, Any]]:
    """
    Make an HTTP request to the Guacamole API with authentication.

    Parameters
    ----------
    guac_client : Any
        The Guacamole client instance providing authentication details.
    url : str
        The URL for the API request.
    method : str, optional
        The HTTP method (e.g., "GET", "POST", "PATCH"). Defaults to "GET".
    params : Optional[Dict[str, Any]], optional
        Query parameters to include in the request. Defaults to None.
    payload : Union[Dict[str, Any], List[Any], None], optional
        The JSON payload for the request body. Defaults to None.
    token : Optional[str], optional
        The authentication token. Defaults to guac_client.token if None.
    verify : Optional[bool], optional
        Whether to verify SSL certificates. Defaults to guac_client.verify if None.
    allow_redirects : bool, optional
        Whether to allow HTTP redirects. Defaults to True.
    cookies : Optional[Dict[str, Any]], optional
        Cookies to include in the request. Defaults to guac_client.cookies if None.
    json_response : bool, optional
        Whether to parse the response as JSON. Defaults to True.

    Returns
    -------
    Union[requests.Response, Dict[str, Any]]
        The HTTP response or parsed JSON dictionary (200 OK or other status).

    Raises
    ------
    requests.HTTPError
        If the HTTP request fails.
    JSONDecodeError
        If json_response is True and the response cannot be parsed as JSON.
    """
    params = params or {}
    token = token or guac_client.token
    verify = verify if verify is not None else guac_client.verify
    cookies = cookies or guac_client.cookies

    params["token"] = token

    logger.debug(f"{method} {url} - Params: {params} - Payload: {payload}")
    response = requests.request(
        method=method,
        url=url,
        params=params,
        json=payload,
        verify=verify,
        allow_redirects=allow_redirects,
        cookies=cookies,
    )
    if not response.ok:
        if response.status_code == 404:
            logger.debug(f"Request failed with status 404: {response.content}")
        else:
            logger.error(
                f"Request failed with status {response.status_code}: {response.content}"
            )
    response.raise_for_status()
    if json_response:
        try:
            return response.json()
        except JSONDecodeError:
            logger.error("Could not decode JSON response")
            raise
    return response

def validate_payload(payload: Dict[str, Any], template: Dict[str, Any], allow_partial: bool = False) -> None:
    """
    Validate a payload against a template, ensuring required fields are present.

    Parameters
    ----------
    payload : Dict[str, Any]
        The payload to validate.
    template : Dict[str, Any]
        The template dictionary with expected structure.
    allow_partial : bool, optional
        If True, allows missing top-level fields and nested dictionary keys (e.g., 'attributes').
        Defaults to False.

    Raises
    ------
    ValueError
        If required fields are missing or types are incorrect when allow_partial=False.
    """
    for key, value in template.items():
        if key not in payload and not allow_partial:
            raise ValueError(f"Missing required field: {key}")
        if isinstance(value, dict) and key in payload and isinstance(payload[key], dict):
            # Allow partial nested dictionaries (e.g., 'attributes') even when allow_partial=False
            # to support optional fields like 'disabled' in user creation
            validate_payload(payload[key], value, allow_partial=True)
        elif value is not None and payload.get(key) is None and not allow_partial:
            raise ValueError(f"Field {key} cannot be None")

def get_hotp_token(
    secret: str,
    intervals_no: int,
) -> int:
    """
    Generate an HOTP token for authentication.

    Parameters
    ----------
    secret : str
        The base32-encoded secret key.
    intervals_no : int
        The counter value for HOTP generation.

    Returns
    -------
    int
        The generated HOTP token.
    """
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = bytes(hmac.new(key, msg, hashlib.sha1).digest())
    o = h[19] & 15
    return (struct.unpack(">I", h[o : o + 4])[0] & 0x7FFFFFFF) % 1000000

def get_totp_token(secret: str) -> str:
    """
    Generate a TOTP token for two-factor authentication.

    Parameters
    ----------
    secret : str
        The base32-encoded secret key.

    Returns
    -------
    str
        The 6-digit TOTP token, padded with zeros if necessary.

    Examples
    --------
    >>> secret = "JBSWY3DPEHPK3PXP"
    >>> token = get_totp_token(secret)
    """
    value = get_hotp_token(secret, intervals_no=int(time.time()) // 30)
    return str(value).rjust(6, "0")

def _find_by_name(
    guac_client: Any,
    data: Dict[str, Any],
    name: str,
    key: str,
    child_key: str,
    regex: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Recursively search for an item by name in a nested dictionary.

    Parameters
    ----------
    guac_client : Any
        The Guacamole client instance.
    data : Dict[str, Any]
        The dictionary to search (e.g., connection or group data).
    name : str
        The name of the item to find.
    key : str
        The key for direct items (e.g., "childConnections" or "childConnectionGroups").
    child_key : str
        The key for nested groups (e.g., "childConnectionGroups").
    regex : bool, optional
        Whether to use regex matching for the name. Defaults to False.

    Returns
    -------
    Optional[Dict[str, Any]]
        The item dictionary if found, else None.
    """
    if key not in data:
        if child_key in data:
            for child in data[child_key]:
                result = _find_by_name(
                    guac_client, child, name, key, child_key, regex
                )
                if result:
                    return result
    else:
        children = data[key]
        if regex:
            result = [x for x in children if re.search(name, x["name"])]
        else:
            result = [x for x in children if x["name"] == name]
        if result:
            return result[0]
        if child_key in data:
            for child in data[child_key]:
                result = _find_by_name(
                    guac_client, child, name, key, child_key, regex
                )
                if result:
                    return result
    if (regex and re.search(name, data["name"])) or (
        not regex and data["name"] == name
    ):
        return data
    return None

def _find_connection_by_name(
    guac_client: Any,
    connection_data: Dict[str, Any],
    name: str,
    regex: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Recursively search for a connection by name in a connection group.

    Parameters
    ----------
    guac_client : Any
        The Guacamole client instance.
    connection_data : Dict[str, Any]
        The connection group dictionary to search.
    name : str
        The name of the connection to find.
    regex : bool, optional
        Whether to use regex matching for the name. Defaults to False.

    Returns
    -------
    Optional[Dict[str, Any]]
        The connection dictionary if found, else None.
    """
    return _find_by_name(
        guac_client,
        connection_data,
        name,
        "childConnections",
        "childConnectionGroups",
        regex,
    )

def _find_connection_group_by_name(
    guac_client: Any,
    group_data: Dict[str, Any],
    name: str,
    regex: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Recursively search for a connection group by name.

    Parameters
    ----------
    guac_client : Any
        The Guacamole client instance.
    group_data : Dict[str, Any]
        The connection group dictionary to search.
    name : str
        The name of the connection group to find.
    regex : bool, optional
        Whether to use regex matching for the name. Defaults to False.

    Returns
    -------
    Optional[Dict[str, Any]]
        The connection group dictionary if found, else None.
    """
    return _find_by_name(
        guac_client,
        group_data,
        name,
        "childConnectionGroups",
        "childConnectionGroups",
        regex,
    )

def get_connection_group_by_name(
    guac_client: Any,
    name: str,
    regex: bool = False,
    datasource: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get a connection group by its name.

    Parameters
    ----------
    guac_client : Any
        The Guacamole client instance.
    name : str
        The name of the connection group to find.
    regex : bool, optional
        Whether to use regex matching for the name. Defaults to False.
    datasource : Optional[str], optional
        The data source identifier. Defaults to guac_client.primary_datasource if None.

    Returns
    -------
    Optional[Dict[str, Any]]
        The connection group dictionary if found, else None.

    Examples
    --------
    >>> client = Guacamole(hostname="guacamole.example.com", username="admin", password="secret")
    >>> group = client.get_connection_group_by_name("Root Group")
    """
    if not datasource:
        datasource = guac_client.primary_datasource
    cons = guac_client.get_connections(datasource)
    return _find_connection_group_by_name(guac_client, cons, name, regex)
