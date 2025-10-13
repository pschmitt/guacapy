Guacapy API Documentation
This document details the behavior of the Apache Guacamole REST API as implemented in guacapy, based on testing with Guacamole 1.6.0. It supplements the unofficial documentation at:https://github.com/ridvanaltun/guacamole-rest-api-documentation
Table of Contents

Notes
Usage Examples
Users
User Groups
Connections
Connection Groups
Sharing Profiles
Active Connections
Schema
Permissions

Notes

The /api/session/ext/guacamole/languages endpoint returns 404 in Guacamole 1.6.0, likely due to a missing extension (e.g., guacamole-auth-jdbc-mysql) or version incompatibility. It is excluded from this wrapper as it appears related to UI language settings.
The ROOT connection group may not appear in ConnectionGroupManager.list() responses, contrary to documentation expectations. Use ConnectionGroupManager.get_by_name("ROOT") to retrieve it.
The UserGroupManager.delete method may fail with a 500 error due to a known SQL syntax issue in Guacamole 1.6.0 (GUACAMOLE-2088). Workaround: Manually delete via SQL: DELETE FROM guacamole_entity WHERE type = 'USER_GROUP' AND name = 'group_name'.

Usage Examples
Below are runnable examples for common tasks using guacapy.
Creating a User
from guacapy import Guacamole
from copy import deepcopy

client = Guacamole(
    hostname="192.168.11.53",
    username="guacadmin",
    password="abAB12!@",
    connection_protocol="https",
    ssl_verify=False,
    connection_port=8443
)
user_manager = client.users
payload = deepcopy(user_manager.USER_TEMPLATE)
payload.update({
    "username": "testuser",
    "password": "securepass",
    "attributes": {"guac-email-address": "test@example.com"}
})
user = user_manager.create(payload)
print(user)

Creating an RDP Connection
from guacapy import Guacamole
from copy import deepcopy

client = Guacamole(
    hostname="192.168.11.53",
    username="guacadmin",
    password="abAB12!@",
    connection_protocol="https",
    ssl_verify=False,
    connection_port=8443
)
conn_manager = client.connections
payload = deepcopy(conn_manager.RDP_TEMPLATE)
payload.update({
    "name": "testrdp",
    "parameters": {
        "hostname": "localhost",
        "port": "3389",
        "username": "admin",
        "password": "secret"
    }
})
connection = conn_manager.create(payload)
print(connection)

Assigning a User to a Connection
from guacapy import Guacamole

client = Guacamole(
    hostname="192.168.11.53",
    username="guacadmin",
    password="abAB12!@",
    connection_protocol="https",
    ssl_verify=False,
    connection_port=8443
)
response = client.users.assign_connection("testuser", "1", permission="READ")
print(response.status_code)  # 204

Creating a User Group
from guacapy import Guacamole
from copy import deepcopy

client = Guacamole(
    hostname="192.168.11.53",
    username="guacadmin",
    password="abAB12!@",
    connection_protocol="https",
    ssl_verify=False,
    connection_port=8443
)
group_manager = client.user_groups
payload = deepcopy(group_manager.GROUP_TEMPLATE)
payload.update({"identifier": "testgroup"})
group = group_manager.create(payload)
print(group)

Adding a User to a User Group
from guacapy import Guacamole

client = Guacamole(
    hostname="192.168.11.53",
    username="guacadmin",
    password="abAB12!@",
    connection_protocol="https",
    ssl_verify=False,
    connection_port=8443
)
response = client.user_groups.edit_members("testgroup", [{"op": "add", "path": "/", "value": "testuser"}])
print(response.status_code)  # 204

Users
GET /api/session/data/{data_source}/users

Description: Retrieves all users in the data source.
Response: Dictionary mapping usernames to details (e.g., {'guacadmin': {'username': 'guacadmin', 'attributes': {...}, ...}}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.


Payload Template: See UserManager.USER_TEMPLATE:{
    "username": "",  # Required
    "password": "",  # Required for create
    "attributes": {
        "disabled": "",  # Optional
        "expired": "",  # Optional
        "access-window-start": "",  # Optional
        "access-window-end": "",  # Optional
        "valid-from": "",  # Optional
        "valid-until": "",  # Optional
        "timezone": null,  # Optional
        "guac-full-name": "",  # Optional
        "guac-organization": "",  # Optional
        "guac-organizational-role": "",  # Optional
        "guac-email-address": ""  # Optional
    }
}



GET /api/session/data/{data_source}/users/{username}

Description: Retrieves details for a specific user.
Response: Dictionary with username, attributes, etc. (e.g., {'username': 'guacadmin', 'attributes': {'guac-email-address': 'admin@example.com'}, ...}).
Status Codes:
200: Success.
404: User not found.
401: Unauthorized.



POST /api/session/data/{data_source}/users

Description: Creates a new user.
Payload: See UserManager.USER_TEMPLATE.
Response: Created user details (e.g., {'username': 'testuser', 'attributes': {...}, ...}).
Status Codes:
200: Success.
400: User already exists or invalid payload.
401: Unauthorized.



PUT /api/session/data/{data_source}/users/{username}

Description: Updates an existing user.
Payload: See UserManager.USER_TEMPLATE.
Response: 204 No Content.
Status Codes:
204: Success.
404: User not found.
400: Invalid payload.



DELETE /api/session/data/{data_source}/users/{username}

Description: Deletes a user.
Response: 204 No Content.
Status Codes:
204: Success.
404: User not found.
401: Unauthorized.



GET /api/session/data/{data_source}/users/{username}/permissions

Description: Retrieves permissions for a specific user.
Response: Dictionary with system and connection permissions (e.g., {'systemPermissions': [...], 'connectionPermissions': {...}, ...}).
Status Codes:
200: Success.
404: User not found.
401: Unauthorized.



GET /api/session/data/{data_source}/users/{username}/effectivePermissions

Description: Retrieves effective permissions for a specific user.
Response: Dictionary with effective permissions (e.g., {'systemPermissions': [...], 'connectionPermissions': {...}, ...}).
Status Codes:
200: Success.
404: User not found.
401: Unauthorized.



GET /api/session/data/{data_source}/users/{username}/userGroups

Description: Retrieves user groups a specific user belongs to.
Response: List of group identifiers (e.g., ['netadmins']).
Status Codes:
200: Success.
404: User not found.
401: Unauthorized.



GET /api/session/data/{data_source}/users/{username}/history

Description: Retrieves connection history for a specific user.
Response: List of history entries (e.g., [{'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', ...}, ...]).
Status Codes:
200: Success.
404: User not found.
401: Unauthorized.



PATCH /api/session/data/{data_source}/users/{username}/userGroups

Description: Assigns or removes a user from a user group.
Payload: [{"op": "add", "path": "/", "value": "group_name"}].
Response: 204 No Content.
Status Codes:
204: Success.
404: User or group not found.
400: Invalid payload.
401: Unauthorized.



PATCH /api/session/data/{data_source}/users/{username}/permissions

Description: Assigns or revokes permissions (e.g., connection or connection group access) for a user.
Payload: [{"op": "add", "path": "/connectionPermissions/{connection}", "value": "READ"}].
Response: 204 No Content.
Status Codes:
204: Success.
404: User or connection not found.
400: Invalid payload.
401: Unauthorized.



PUT /api/session/data/{data_source}/users/{username}/password

Description: Updates a user’s password.
Payload: {"oldPassword": "old_pass", "newPassword": "new_pass"}.
Response: 204 No Content.
Status Codes:
204: Success.
400: Invalid payload or incorrect old password.
401: Unauthorized.



GET /api/session/data/self

Description: Retrieves details for the currently authenticated user.
Response: Dictionary with user details (e.g., {'username': 'guacadmin', 'attributes': {...}, ...}).
Status Codes:
200: Success.
401: Unauthorized.



User Groups
GET /api/session/data/{data_source}/userGroups

Description: Retrieves all user groups in the data source.
Expected Response (per USER_GROUPS.md): List of group identifiers (e.g., ['netadmins', 'sysadmins']).
Actual Response: Dictionary mapping group identifiers to details (e.g., {'netadmins': {'identifier': 'netadmins', 'disabled': False, 'attributes': {}}, ...}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.


Notes: The response format differs from the documentation, returning a dictionary instead of a list.
Payload Template: See UserGroupManager.GROUP_TEMPLATE:{
    "identifier": "",  # Required
    "attributes": {
        "disabled": ""  # Optional
    }
}



GET /api/session/data/{data_source}/userGroups/{identifier}

Description: Retrieves details for a specific user group.
Response: Dictionary with identifier, disabled, and attributes (e.g., {'identifier': 'netadmins', 'disabled': False, 'attributes': {}}).
Status Codes:
200: Success.
404: Group not found.
401: Unauthorized.



POST /api/session/data/{data_source}/userGroups

Description: Creates a new user group.
Payload: See UserGroupManager.GROUP_TEMPLATE.
Response: Created group details (e.g., {'identifier': 'testgroup', 'disabled': False, 'attributes': {}}).
Status Codes:
200: Success.
400: Group already exists.
401: Unauthorized.



PUT /api/session/data/{data_source}/userGroups/{identifier}

Description: Updates an existing user group.
Payload: See UserGroupManager.GROUP_TEMPLATE.
Response: 204 No Content.
Status Codes:
204: Success.
404: Group not found.
400: Invalid payload.



DELETE /api/session/data/{data_source}/userGroups/{identifier}

Description: Deletes a user group.
Response: 204 No Content.
Status Codes:
204: Success.
404: Group not found.
500: Internal server error.


Notes: Fails with 500 in Guacamole 1.6.0 due to SQL syntax error in MySQL JDBC module (GUACAMOLE-2088).

GET /api/session/data/{data_source}/userGroups/{identifier}/memberUsers

Description: Retrieves member users of a specific user group.
Response: Dictionary mapping usernames to user details (e.g., {'daxm': {'username': 'daxm', 'attributes': {...}, ...}, ...}).
Status Codes:
200: Success.
404: Group not found.
401: Unauthorized.



PATCH /api/session/data/{data_source}/userGroups/{identifier}/memberUsers

Description: Adds or removes members from a user group.
Payload: [{"op": "add", "path": "/", "value": "username"}].
Response: 204 No Content.
Status Codes:
204: Success.
404: Group or user not found.
400: Invalid payload.
401: Unauthorized.



Connections
GET /api/session/data/{data_source}/connections

Description: Retrieves all connections in the data source.
Response: Dictionary mapping connection identifiers to details (e.g., {'1': {'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.


Payload Template: See ConnectionManager.RDP_TEMPLATE, ConnectionManager.SSH_TEMPLATE, ConnectionManager.VNC_TEMPLATE for protocol-specific structures.# Example: RDP_TEMPLATE
{
    "name": "",  # Required
    "parentIdentifier": "ROOT",  # Required
    "protocol": "rdp",  # Required
    "attributes": {
        "max-connections": "",  # Optional
        "max-connections-per-user": "",  # Optional
        "weight": "",  # Optional
        "failover-only": "",  # Optional
        "guacd-port": "",  # Optional
        "guacd-encryption": "",  # Optional
        "guacd-hostname": ""  # Optional
    },
    "parameters": {
        "hostname": "",  # Required
        "port": "3389",  # Optional
        "username": "",  # Optional
        "password": "",  # Optional
        "security": "rdp",  # Optional
        "disable-audio": "",  # Optional
        "server-layout": "",  # Optional
        "domain": "",  # Optional
        "enable-font-smoothing": "",  # Optional
        "ignore-cert": "",  # Optional
        "console": "",  # Optional
        "width": "",  # Optional
        "height": "",  # Optional
        "dpi": "",  # Optional
        "color-depth": "",  # Optional
        "console-audio": "",  # Optional
        "enable-printing": "",  # Optional
        "enable-drive": "",  # Optional
        "create-drive-path": "",  # Optional
        "enable-wallpaper": "",  # Optional
        "enable-theming": "",  # Optional
        "enable-full-window-drag": "",  # Optional
        "enable-desktop-composition": "",  # Optional
        "enable-menu-animations": "",  # Optional
        "preconnection-id": "",  # Optional
        "enable-sftp": "",  # Optional
        "sftp-port": ""  # Optional
    }
}



GET /api/session/data/{data_source}/connections/{identifier}

Description: Retrieves details for a specific connection.
Response: Dictionary with identifier, name, protocol, etc. (e.g., {'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}).
Status Codes:
200: Success.
404: Connection not found.
401: Unauthorized.



GET /api/session/data/{data_source}/connections/{identifier}/parameters

Description: Retrieves parameters for a specific connection.
Response: Dictionary with connection parameters (e.g., {'hostname': 'localhost', 'port': '22', 'username': 'admin', ...}).
Status Codes:
200: Success.
404: Connection not found.
401: Unauthorized.



POST /api/session/data/{data_source}/connections

Description: Creates a new connection.
Payload: See ConnectionManager.RDP_TEMPLATE, ConnectionManager.SSH_TEMPLATE, or ConnectionManager.VNC_TEMPLATE.
Response: Created connection details (e.g., {'identifier': '2', 'name': 'testconnection', ...}).
Status Codes:
200: Success.
400: Connection already exists or invalid payload.
401: Unauthorized.



PUT /api/session/data/{data_source}/connections/{identifier}

Description: Updates an existing connection.
Payload: See ConnectionManager.RDP_TEMPLATE, ConnectionManager.SSH_TEMPLATE, or ConnectionManager.VNC_TEMPLATE.
Response: 204 No Content.
Status Codes:
204: Success.
404: Connection not found.
400: Invalid payload.



DELETE /api/session/data/{data_source}/connections/{identifier}

Description: Deletes a connection.
Response: 204 No Content.
Status Codes:
204: Success.
404: Connection not found.
401: Unauthorized.



Connection Groups
GET /api/session/data/{data_source}/connectionGroups

Description: Retrieves all connection groups in the data source.
Response: Dictionary mapping group identifiers to details (e.g., {'1': {'identifier': '1', 'name': 'bh01 (Main Hospital)', 'type': 'ORGANIZATIONAL', ...}}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.


Notes: The ROOT group may not appear in the response. Use ConnectionGroupManager.get_by_name("ROOT") to retrieve it.
Payload Template: See ConnectionGroupManager.ORG_TEMPLATE:{
    "name": "",  # Required
    "parentIdentifier": "ROOT",  # Required
    "type": "ORGANIZATIONAL",  # Required
    "attributes": {
        "max-connections": "",  # Optional
        "max-connections-per-user": ""  # Optional
    }
}



GET /api/session/data/{data_source}/connectionGroups/{identifier}

Description: Retrieves details for a specific connection group.
Response: Dictionary with identifier, name, type, etc. (e.g., {'identifier': '1', 'name': 'bh01 (Main Hospital)', 'type': 'ORGANIZATIONAL', ...}).
Status Codes:
200: Success.
404: Group not found.
401: Unauthorized.



POST /api/session/data/{data_source}/connectionGroups

Description: Creates a new connection group.
Payload: See ConnectionGroupManager.ORG_TEMPLATE.
Response: Created group details (e.g., {'identifier': '2', 'name': 'testgroup', ...}).
Status Codes:
200: Success.
400: Group already exists or invalid payload.
401: Unauthorized.



PUT /api/session/data/{data_source}/connectionGroups/{identifier}

Description: Updates an existing connection group.
Payload: See ConnectionGroupManager.ORG_TEMPLATE.
Response: 204 No Content.
Status Codes:
204: Success.
404: Group not found.
400: Invalid payload.



DELETE /api/session/data/{data_source}/connectionGroups/{identifier}

Description: Deletes a connection group.
Response: 204 No Content.
Status Codes:
204: Success.
404: Group not found.
401: Unauthorized.



Sharing Profiles
GET /api/session/data/{data_source}/sharingProfiles

Description: Retrieves all sharing profiles in the data source.
Response: Dictionary mapping profile identifiers to details (e.g., {'1': {'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.


Payload Template: See SharingProfileManager.PROFILE_TEMPLATE:{
    "name": "",  # Required
    "primaryConnectionIdentifier": "",  # Required
    "parameters": {"read-only": ""},  # Optional
    "attributes": {}  # Optional
}



GET /api/session/data/{data_source}/sharingProfiles/{identifier}

Description: Retrieves details for a specific sharing profile.
Response: Dictionary with identifier, name, primaryConnectionIdentifier, etc. (e.g., {'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}).
Status Codes:
200: Success.
404: Profile not found.
401: Unauthorized.



GET /api/session/data/{data_source}/sharingProfiles/{identifier}/parameters

Description: Retrieves parameters for a specific sharing profile.
Response: Dictionary with parameters (e.g., {'read-only': '', ...}).
Status Codes:
200: Success.
404: Profile not found.
401: Unauthorized.



POST /api/session/data/{data_source}/sharingProfiles

Description: Creates a new sharing profile.
Payload: See SharingProfileManager.PROFILE_TEMPLATE.
Response: Created profile details (e.g., {'identifier': '2', 'name': 'testprofile', ...}).
Status Codes:
200: Success.
400: Profile already exists or invalid payload.
401: Unauthorized.



PUT /api/session/data/{data_source}/sharingProfiles/{identifier}

Description: Updates an existing sharing profile.
Payload: See SharingProfileManager.PROFILE_TEMPLATE.
Response: 204 No Content.
Status Codes:
204: Success.
404: Profile not found.
400: Invalid payload.



DELETE /api/session/data/{data_source}/sharingProfiles/{identifier}

Description: Deletes a sharing profile.
Response: 204 No Content.
Status Codes:
204: Success.
404: Profile not found.
401: Unauthorized.



Active Connections
GET /api/session/data/{data_source}/activeConnections

Description: Retrieves all active connections in the data source.
Response: Dictionary mapping connection identifiers to details (e.g., {'1': {'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', 'username': 'daxm', ...}}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.



GET /api/session/data/{data_source}/activeConnections/{identifier}

Description: Retrieves details for a specific active connection.
Response: Dictionary with identifier, startDate, remoteHost, username, etc. (e.g., {'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', 'username': 'daxm', ...}).
Status Codes:
200: Success.
404: Connection not found.
401: Unauthorized.



DELETE /api/session/data/{data_source}/activeConnections/{identifier}

Description: Terminates an active connection.
Response: 204 No Content.
Status Codes:
204: Success.
404: Connection not found.
401: Unauthorized.



Schema
GET /api/session/data/{data_source}/schema/protocols

Description: Retrieves supported connection protocols.
Response: Dictionary mapping protocol names to details (e.g., {'ssh': {'name': 'ssh', 'attributes': {...}}, 'rdp': {...}}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.



GET /api/session/data/{data_source}/schema/userAttributes

Description: Retrieves available user attributes.
Response: Dictionary of user attributes and their properties (e.g., {'guac-email-address': {'type': 'STRING'}, 'guac-full-name': {'type': 'STRING'}, ...}).
Status Codes:
200: Success.
401: Unauthorized.
403: Insufficient permissions.



Permissions
PATCH /api/session/data/{data_source}/users/{username}/permissions

Description: Assigns or revokes system permissions for a user.
Payload: [{"op": "add", "path": "/systemPermissions", "value": "{permission}"}].
Response: 204 No Content.
Status Codes:
204: Success.
404: User not found.
400: Invalid permission or payload.
401: Unauthorized.


Notes: Valid permissions include CREATE_USER, CREATE_USER_GROUP, CREATE_CONNECTION, CREATE_CONNECTION_GROUP, CREATE_SHARING_PROFILE, ADMINISTER. The value field must be a string, not a list.
