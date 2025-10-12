# Guacapy API Documentation

This document tracks the actual behavior of the Apache Guacamole REST API based on testing with `guacapy`, supplementing the unofficial documentation at:
https://github.com/ridvanaltun/guacamole-rest-api-documentation

## Notes
- The `/api/session/ext/guacamole/languages` endpoint returned 404 in Guacamole 1.6.0, likely due to a missing extension (e.g., `guacamole-auth-jdbc-mysql`) or version incompatibility. It is excluded from this wrapper as it appears related to UI language settings.

## Users

### GET /api/session/data/{data_source}/users
- **Description**: Retrieves all users in the data source.
- **Response**: Dictionary mapping usernames to details (e.g., `{'guacadmin': {'username': 'guacadmin', 'attributes': {...}, ...}}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.

### GET /api/session/data/{data_source}/users/{username}
- **Description**: Retrieves details for a specific user.
- **Response**: Dictionary with `username`, `attributes`, etc. (e.g., `{'username': 'guacadmin', 'attributes': {'guac-email-address': 'admin@example.com'}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: User not found.
  - 401: Unauthorized.

### POST /api/session/data/{data_source}/users
- **Description**: Creates a new user.
- **Payload**: `{"username": "user_name", "password": "password", "attributes": {"disabled": false, "guac-email-address": "email@example.com"}}`.
- **Response**: Created user details (e.g., `{'username': 'testuser', 'attributes': {...}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 400: User already exists or invalid payload.
  - 401: Unauthorized.

### PUT /api/session/data/{data_source}/users/{username}
- **Description**: Updates an existing user.
- **Payload**: `{"username": "user_name", "attributes": {"guac-email-address": "updated@example.com"}}`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: User not found.
  - 400: Invalid payload.

### DELETE /api/session/data/{data_source}/users/{username}
- **Description**: Deletes a user.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: User not found.
  - 401: Unauthorized.

### GET /api/session/data/{data_source}/users/{username}/permissions
- **Description**: Retrieves permissions for a specific user.
- **Response**: Dictionary with system and connection permissions (e.g., `{'systemPermissions': [...], 'connectionPermissions': {...}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: User not found.
  - 401: Unauthorized.

### GET /api/session/data/{data_source}/users/{username}/effectivePermissions
- **Description**: Retrieves effective permissions for a specific user.
- **Response**: Dictionary with effective permissions (e.g., `{'systemPermissions': [...], 'connectionPermissions': {...}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: User not found.
  - 401: Unauthorized.

### GET /api/session/data/{data_source}/users/{username}/userGroups
- **Description**: Retrieves user groups a specific user belongs to.
- **Response**: List of group identifiers (e.g., `['netadmins']`).
- **Status Codes**:
  - 200: Success.
  - 404: User not found.
  - 401: Unauthorized.

### GET /api/session/data/{data_source}/users/{username}/history
- **Description**: Retrieves connection history for a specific user.
- **Response**: List of history entries (e.g., `[{'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', ...}, ...]`).
- **Status Codes**:
  - 200: Success.
  - 404: User not found.
  - 401: Unauthorized.

### PATCH /api/session/data/{data_source}/users/{username}/userGroups
- **Description**: Assigns or removes a user from a user group.
- **Payload**: `[{"op": "add", "path": "/", "value": "group_name"}]`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: User or group not found.
  - 400: Invalid payload.
  - 401: Unauthorized.

### PATCH /api/session/data/{data_source}/users/{username}/permissions
- **Description**: Assigns or revokes permissions (e.g., connection or connection group access) for a user.
- **Payload**: `[{"op": "add", "path": "/connectionPermissions/{connection}", "value": "READ"}]`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: User or connection not found.
  - 400: Invalid payload.
  - 401: Unauthorized.

### PUT /api/session/data/{data_source}/users/{username}/password
- **Description**: Updates a user’s password.
- **Payload**: `{"oldPassword": "old_pass", "newPassword": "new_pass"}`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 400: Invalid payload or incorrect old password.
  - 401: Unauthorized.

### GET /api/session/data/self
- **Description**: Retrieves details for the currently authenticated user.
- **Response**: Dictionary with user details (e.g., `{'username': 'guacadmin', 'attributes': {...}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.

## User Groups
### GET /api/session/data/{data_source}/userGroups
- **Description**: Retrieves all user groups in the data source.
- **Expected Response (per USER_GROUPS.md)**: List of group identifiers (e.g., `['netadmins', 'sysadmins']`).
- **Actual Response**: Dictionary mapping group identifiers to details (e.g., `{'netadmins': {'identifier': 'netadmins', 'disabled': False, 'attributes': {}}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.
- **Notes**: The response format differs from the documentation, returning a dictionary instead of a list.

### GET /api/session/data/{data_source}/userGroups/{identifier}
- **Description**: Retrieves details for a specific user group.
- **Response**: Dictionary with `identifier`, `disabled`, and `attributes` (e.g., `{'identifier': 'netadmins', 'disabled': False, 'attributes': {}}`).
- **Status Codes**:
  - 200: Success.
  - 404: Group not found.
  - 401: Unauthorized.

### POST /api/session/data/{data_source}/userGroups
- **Description**: Creates a new user group.
- **Payload**: `{"identifier": "group_name", "attributes": {"disabled": false}}`.
- **Response**: Created group details (e.g., `{'identifier': 'testgroup', 'disabled': False, 'attributes': {}}`).
- **Status Codes**:
  - 200: Success.
  - 400: Group already exists.
  - 401: Unauthorized.

### PUT /api/session/data/{data_source}/userGroups/{identifier}
- **Description**: Updates an existing user group.
- **Payload**: `{"identifier": "group_name", "attributes": {"disabled": true}}`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Group not found.
  - 400: Invalid payload.

### DELETE /api/session/data/{data_source}/userGroups/{identifier}
- **Description**: Deletes a user group.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Group not found.
  - 500: Internal server error.
- **Notes**: Fails with 500 in Guacamole 1.6.0 due to SQL syntax error in MySQL JDBC module (GUACAMOLE-2088).

## Connections
### GET /api/session/data/{data_source}/connections
- **Description**: Retrieves all connections in the data source.
- **Response**: Dictionary mapping connection identifiers to details (e.g., `{'1': {'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.

### GET /api/session/data/{data_source}/connections/{identifier}
- **Description**: Retrieves details for a specific connection.
- **Response**: Dictionary with `identifier`, `name`, `protocol`, etc. (e.g., `{'identifier': '1', 'name': 'test', 'protocol': 'ssh', ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: Connection not found.
  - 401: Unauthorized.

### POST /api/session/data/{data_source}/connections
- **Description**: Creates a new connection.
- **Payload**: `{"name": "connection_name", "parentIdentifier": "ROOT", "protocol": "ssh", "parameters": {"hostname": "localhost", "port": "22"}, "attributes": {}}`.
- **Response**: Created connection details (e.g., `{'identifier': '2', 'name': 'testconnection', ...}`).
- **Status Codes**:
  - 200: Success.
  - 400: Connection already exists or invalid payload.
  - 401: Unauthorized.

### PUT /api/session/data/{data_source}/connections/{identifier}
- **Description**: Updates an existing connection.
- **Payload**: `{"identifier": "2", "name": "testconnection_updated", "parentIdentifier": "ROOT", "protocol": "ssh", "parameters": {"hostname": "localhost", "port": "22"}, "attributes": {}}`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Connection not found.
  - 400: Invalid payload.

### DELETE /api/session/data/{data_source}/connections/{identifier}
- **Description**: Deletes a connection.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Connection not found.
  - 401: Unauthorized.

## Connection Groups
### GET /api/session/data/{data_source}/connectionGroups
- **Description**: Retrieves all connection groups in the data source.
- **Response**: Dictionary mapping group identifiers to details (e.g., `{'1': {'identifier': '1', 'name': 'bh01 (Main Hospital)', 'type': 'ORGANIZATIONAL', ...}}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.
- **Notes**: The `ROOT` group may not appear in the response, unlike documentation expectations.

### GET /api/session/data/{data_source}/connectionGroups/{identifier}
- **Description**: Retrieves details for a specific connection group.
- **Response**: Dictionary with `identifier`, `name`, `type`, etc. (e.g., `{'identifier': '1', 'name': 'bh01 (Main Hospital)', 'type': 'ORGANIZATIONAL', ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: Group not found.
  - 401: Unauthorized.

### POST /api/session/data/{data_source}/connectionGroups
- **Description**: Creates a new connection group.
- **Payload**: `{"name": "group_name", "parentIdentifier": "ROOT", "type": "ORGANIZATIONAL", "attributes": {}}`.
- **Response**: Created group details (e.g., `{'identifier': '2', 'name': 'testgroup', ...}`).
- **Status Codes**:
  - 200: Success.
  - 400: Group already exists or invalid payload.
  - 401: Unauthorized.

### PUT /api/session/data/{data_source}/connectionGroups/{identifier}
- **Description**: Updates an existing connection group.
- **Payload**: `{"identifier": "2", "name": "testgroup_updated", "parentIdentifier": "ROOT", "type": "ORGANIZATIONAL", "attributes": {}}`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Group not found.
  - 400: Invalid payload.

### DELETE /api/session/data/{data_source}/connectionGroups/{identifier}
- **Description**: Deletes a connection group.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Group not found.
  - 401: Unauthorized.

## Sharing Profiles
### GET /api/session/data/{data_source}/sharingProfiles
- **Description**: Retrieves all sharing profiles in the data source.
- **Response**: Dictionary mapping profile identifiers to details (e.g., `{'1': {'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.

### GET /api/session/data/{data_source}/sharingProfiles/{identifier}
- **Description**: Retrieves details for a specific sharing profile.
- **Response**: Dictionary with `identifier`, `name`, `primaryConnectionIdentifier`, etc. (e.g., `{'identifier': '1', 'name': 'share', 'primaryConnectionIdentifier': '1', ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: Profile not found.
  - 401: Unauthorized.

### POST /api/session/data/{data_source}/sharingProfiles
- **Description**: Creates a new sharing profile.
- **Payload**: `{"name": "profile_name", "primaryConnectionIdentifier": "1", "parameters": {}, "attributes": {}}`.
- **Response**: Created profile details (e.g., `{'identifier': '2', 'name': 'testprofile', ...}`).
- **Status Codes**:
  - 200: Success.
  - 400: Profile already exists or invalid payload.
  - 401: Unauthorized.

### PUT /api/session/data/{data_source}/sharingProfiles/{identifier}
- **Description**: Updates an existing sharing profile.
- **Payload**: `{"identifier": "2", "name": "testprofile_updated", "primaryConnectionIdentifier": "1", "parameters": {}, "attributes": {}}`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Profile not found.
  - 400: Invalid payload.

### DELETE /api/session/data/{data_source}/sharingProfiles/{identifier}
- **Description**: Deletes a sharing profile.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Profile not found.
  - 401: Unauthorized.

## Active Connections
### GET /api/session/data/{data_source}/activeConnections
- **Description**: Retrieves all active connections in the data source.
- **Response**: Dictionary mapping connection identifiers to details (e.g., `{'1': {'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', 'username': 'daxm', ...}}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.

### GET /api/session/data/{data_source}/activeConnections/{identifier}
- **Description**: Retrieves details for a specific active connection.
- **Response**: Dictionary with `identifier`, `startDate`, `remoteHost`, `username`, etc. (e.g., `{'identifier': '1', 'startDate': 1760023106000, 'remoteHost': '172.19.0.5', 'username': 'daxm', ...}`).
- **Status Codes**:
  - 200: Success.
  - 404: Connection not found.
  - 401: Unauthorized.

### DELETE /api/session/data/{data_source}/activeConnections/{identifier}
- **Description**: Terminates an active connection.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: Connection not found.
  - 401: Unauthorized.

## Schema
### GET /api/session/data/{data_source}/schema/protocols
- **Description**: Retrieves supported connection protocols.
- **Response**: Dictionary mapping protocol names to details (e.g., `{'ssh': {'name': 'ssh', 'attributes': {...}}, 'rdp': {...}}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.

### GET /api/session/data/{data_source}/schema/userAttributes
- **Description**: Retrieves available user attributes.
- **Response**: Dictionary of user attributes and their properties (e.g., `{'guac-email-address': {'type': 'STRING'}, 'guac-full-name': {'type': 'STRING'}, ...}`).
- **Status Codes**:
  - 200: Success.
  - 401: Unauthorized.
  - 403: Insufficient permissions.

## Permissions
### PATCH /api/session/data/{data_source}/users/{username}/permissions
- **Description**: Assigns or revokes system permissions for a user.
- **Payload**: `[{"op": "add", "path": "/systemPermissions", "value": "{permission}"}]`.
- **Response**: 204 No Content.
- **Status Codes**:
  - 204: Success.
  - 404: User not found.
  - 400: Invalid permission or payload.
  - 401: Unauthorized.
- **Notes**: Valid permissions include `CREATE_USER`, `CREATE_USER_GROUP`, `CREATE_CONNECTION`, `CREATE_CONNECTION_GROUP`, `CREATE_SHARING_PROFILE`, `ADMINISTER`. The `value` field must be a string, not a list.
