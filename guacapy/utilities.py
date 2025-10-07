import hmac
import base64
import struct
import hashlib
import time
import logging
import re
import requests
from simplejson.scanner import JSONDecodeError

# Get the logger for this module
logger = logging.getLogger(__name__)


def requester(
    method: str,
    url: str,
    params: dict = None,
    token: str = None,
    payload: dict = None,
    verify: bool = True,
    allow_redirects: bool = True,
    cookies: dict = None,
    json_response: bool = True,
):
    if params is None:
        params = []
    if token:
        params += [("token", token)]

    logger.debug(f"{method} {url} - Params: {params}- Payload: {payload}")
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


def get_hotp_token(
    secret,
    intervals_no,
):
    key = base64.b32decode(
        secret,
        True,
    )
    msg = struct.pack(
        ">Q",
        intervals_no,
    )
    h = bytes(hmac.new(key, msg, hashlib.sha1).digest())
    o = h[19] & 15
    h = (struct.unpack(">I", h[o : o + 4])[0] & 0x7FFFFFFF) % 1000000
    return h


def get_totp_token(secret):
    value = get_hotp_token(
        secret,
        intervals_no=int(time.time()) // 30,
    )
    # 6 digits for totp token (pad with 0 char)
    return str(value).rjust(
        6,
        "0",
    )


def _get_connection_by_name(
    self,
    cons,
    name,
    regex=False,
):
    # FIXME This need refactoring (DRY)
    if "childConnections" not in cons:
        if "childConnectionGroups" in cons:
            for c in cons["childConnectionGroups"]:
                res = self._get_connection_by_name(
                    c,
                    name,
                    regex,
                )
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
                    res = self._get_connection_by_name(
                        c,
                        name,
                        regex,
                    )
                    if res:
                        return res
        else:
            return res[0]


def get_history(
    self,
    datasource=None,
):
    if not datasource:
        datasource = self.primary_datasource
    raise NotImplementedError()


def _get_connection_group_by_name(
    self,
    cons,
    name,
    regex=False,
):
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
            res = self._get_connection_group_by_name(
                c,
                name,
                regex,
            )
            if res:
                return res


def get_connection_group_by_name(
    self,
    name,
    regex=False,
    datasource=None,
):
    """
    Get a connection group by its name
    """
    if not datasource:
        datasource = self.primary_datasource
    cons = self.get_connections(datasource)
    return self._get_connection_group_by_name(
        cons,
        name,
        regex,
    )


import logging


def set_log_level(
    level_str: str,
    logger_name: str = "",
) -> None:
    """
    Set the logging level for a specified logger based on a string input.

    Args:
        level_str (str): The logging level as a string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        logger_name (str): The name of the logger to update. Defaults to '' (root logger).

    Raises:
        ValueError: If the provided level string is invalid.
    """
    # Valid logging levels
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Normalize input to uppercase for case-insensitive comparison
    level_str = level_str.upper()

    # Validate the input
    if level_str not in level_map:
        valid_levels = ", ".join(level_map.keys())
        raise ValueError(
            f"Invalid logging level '{level_str}'. Valid options are: {valid_levels}"
        )

    # Get the logger (root logger if logger_name is empty)
    logger = logging.getLogger(logger_name)

    # Set the logging level
    logger.setLevel(level_map[level_str])

    # Log confirmation at the new level
    logger.log(
        level_map[level_str],
        f"Logging level for '{logger_name or 'root'}' set to {level_str}",
    )
