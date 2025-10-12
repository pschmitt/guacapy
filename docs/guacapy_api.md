# Guacapy API Documentation

This document tracks the actual behavior of the Apache Guacamole REST API based on testing with `guacapy`, supplementing the unofficial documentation at:
https://github.com/ridvanaltun/guacamole-rest-api-documentation

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

## To Be Documented
- [ ] Users
