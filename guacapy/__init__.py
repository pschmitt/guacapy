"""
Guacamole API client package.

This module provides the `Guacamole` class as the primary interface for interacting with the
Guacamole REST API, enabling management of users, connections, connection groups, and other
resources through manager classes (e.g., `UserManager`, `ConnectionManager`). The package
version follows a date-based format (major.YYYYMMDD.patch).

This package uses the API endpoints documented as here:
https://github.com/ridvanaltun/guacamole-rest-api-documentation

Examples
--------
>>> from guacapy import Guacamole
>>> client = Guacamole(
...     hostname="guacamole.example.com",
...     username="admin",
...     password="secret",
...     datasource="mysql"
... )
>>> users = client.users.list()  # Access UserManager via client.users
"""

from .client import Guacamole

__all__ = ["Guacamole"]
