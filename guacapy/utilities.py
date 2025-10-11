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
from simplejson.scanner import JSONDecodeError
from typing import Union, Dict, List, Any, Optional

# Get the logger for this module
logger = logging.getLogger(__name__)

def configure_logging(
    level: str = "INFO",
    logger_name: str = "",
    log_file: str = "app.log",
) -> None:
    """
    Configure logging for the application.

    Parameters
    ----------
    level : str, optional
        The logging level (e.g., "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"). Defaults to "INFO".
    logger_name : str, optional
        The name of the logger to configure. Defaults to the root logger.
    log_file : str, optional
        The file to write logs to. Defaults to "app.log".

    Raises
    ------
    ValueError
        If the provided logging level is invalid.
    """
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
        raise ValueError(f"Invalid logging level '{level}'. Valid options are: {valid_levels}")

    my_logger = logging.getLogger(logger_name)
    my_logger.setLevel(level_map[level])
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    my_logger.handlers = [stream_handler, file_handler]
    my_logger.log(level_map[level], f"Logging configured for '{logger_name or 'root'}' at level {level}")

def requester(
    client: Any,
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
    client : Any
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
        The authentication token. Defaults to client.token if None.
    verify : Optional[bool], optional
        Whether to verify SSL certificates. Defaults to client.verify if None.
    allow_redirects : bool, optional
        Whether to allow HTTP redirects. Defaults to True.
    cookies : Optional[Dict[str, Any]], optional
        Cookies to include in the request. Defaults to client.cookies if None.
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
    token = token or client.token
    verify = verify if verify is not None else client.verify
    cookies = cookies or client.cookies

    params["token"] = token

    logger.debug(f"{method} {url} - Params: {params} - Payload: {payload}")
    r = requests.request(
        method=method,
        url=url,
        params=params,
        json=payload,
        verify=verify,
        allow_redirects=allow_redirects,
        cookies=cookies,
    )
    if not r.ok:
        logger.error(f"Request failed with status {r.status_code}: {r.content}")
    r.raise_for_status()
    if json_response:
        try:
            return r.json()
        except JSONDecodeError:
            logger.error("Could not decode JSON response")
            raise
    return r

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

def _get_connection_by_name(
    client: Any,
    cons: Dict[str, Any],
    name: str,
    regex: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Recursively search for a connection by name in a connection group.

    Parameters
    ----------
    client : Any
        The Guacamole client instance.
    cons : Dict[str, Any]
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
    if "childConnections" not in cons:
        if "childConnectionGroups" in cons:
            for c in cons["childConnectionGroups"]:
                res = _get_connection_by_name(client, c, name, regex)
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
                    res = _get_connection_by_name(client, c, name, regex)
                    if res:
                        return res
        else:
            return res[0]
    return None

def get_history(
    client: Any,
    datasource: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Retrieve connection history (not implemented).

    Parameters
    ----------
    client : Any
        The Guacamole client instance.
    datasource : Optional[str], optional
        The data source identifier. Defaults to client.primary_datasource if None.

    Returns
    -------
    Dict[str, Any]
        The connection history (placeholder).

    Raises
    ------
    NotImplementedError
        Always raised, as this function is not yet implemented.
    """
    if not datasource:
        datasource = client.primary_datasource
    raise NotImplementedError("get_history is not yet implemented")

def _get_connection_group_by_name(
    client: Any,
    cons: Dict[str, Any],
    name: str,
    regex: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Recursively search for a connection group by name.

    Parameters
    ----------
    client : Any
        The Guacamole client instance.
    cons : Dict[str, Any]
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
    if (regex and re.search(name, cons["name"])) or (not regex and cons["name"] == name):
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
            res = _get_connection_group_by_name(client, c, name, regex)
            if res:
                return res
    return None

def get_connection_group_by_name(
    client: Any,
    name: str,
    regex: bool = False,
    datasource: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """
    Get a connection group by its name.

    Parameters
    ----------
    client : Any
        The Guacamole client instance.
    name : str
        The name of the connection group to find.
    regex : bool, optional
        Whether to use regex matching for the name. Defaults to False.
    datasource : Optional[str], optional
        The data source identifier. Defaults to client.primary_datasource if None.

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
        datasource = client.primary_datasource
    cons = client.get_connections(datasource)
    return _get_connection_group_by_name(client, cons, name, regex)
