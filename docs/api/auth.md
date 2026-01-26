---
title: Authentication API
icon: lucide/key
---

# Authentication API

The Authentication API provides endpoints for user management, login, token handling, and authentication configuration.

---

## Overview

All authentication endpoints are prefixed with `/api/auth`. When authentication is enabled, most other API endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## Endpoints

### `GET /api/auth/status`

Returns the current authentication status.

#### Response

```json
{
  "enabled": true,
  "has_users": true,
  "setup_skipped": false
}
```

| Field | Type | Description |
|-------|------|-------------|
| `enabled` | boolean | Whether authentication is currently required |
| `has_users` | boolean | Whether any user accounts exist |
| `setup_skipped` | boolean | Whether initial setup was skipped |

---

### `POST /api/auth/login`

Authenticates a user and returns JWT tokens.

#### Request body

```json
{
  "username": "admin",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 401 | Invalid credentials |
| 403 | User account is disabled |

#### Example

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

---

### `POST /api/auth/refresh`

Exchanges a refresh token for new access and refresh tokens.

#### Request body

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 401 | Invalid or expired refresh token |

---

### `POST /api/auth/verify`

Verifies that an access token is valid.

#### Request body

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Response

```json
{
  "valid": true,
  "username": "admin"
}
```

---

### `POST /api/auth/setup`

Creates the first user account and enables authentication. Only works when no users exist.

#### Request body

```json
{
  "username": "admin",
  "password": "yourpassword"
}
```

#### Response

```json
{
  "message": "User created successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Users already exist |
| 422 | Invalid username or password format |

---

### `POST /api/auth/skip-setup`

Skips the initial setup wizard, leaving authentication disabled.

#### Response

```json
{
  "message": "Setup skipped, authentication disabled"
}
```

---

### `POST /api/auth/enable`

Enables authentication. Requires at least one user to exist.

#### Response

```json
{
  "message": "Authentication enabled"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | No users exist - create a user first |

---

### `POST /api/auth/disable`

Disables authentication, allowing unauthenticated access to all endpoints.

!!! danger "Security warning"

    Disabling authentication exposes all DUMB functionality without any access control.

#### Response

```json
{
  "message": "Authentication disabled"
}
```

---

## User management endpoints

These endpoints require authentication when auth is enabled.

### `GET /api/auth/users`

Lists all user accounts.

#### Response

```json
{
  "users": [
    {
      "username": "admin",
      "disabled": false
    },
    {
      "username": "readonly",
      "disabled": true
    }
  ]
}
```

---

### `POST /api/auth/users`

Creates a new user account.

#### Request body

```json
{
  "username": "newuser",
  "password": "userpassword"
}
```

#### Response

```json
{
  "message": "User created successfully",
  "username": "newuser"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Username already exists |
| 422 | Invalid username or password format |

---

### `PUT /api/auth/users/{username}`

Updates a user account (enable/disable).

#### Path parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | string | The username to update |

#### Request body

```json
{
  "disabled": true
}
```

#### Response

```json
{
  "message": "User updated successfully",
  "username": "readonly",
  "disabled": true
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Cannot disable the last active user |
| 404 | User not found |

---

### `DELETE /api/auth/users/{username}`

Deletes a user account.

#### Path parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `username` | string | The username to delete |

#### Response

```json
{
  "message": "User deleted successfully"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Cannot delete the last active user |
| 404 | User not found |

---

## Token structure

JWT tokens contain the following claims:

```json
{
  "sub": "admin",
  "exp": 1704067200,
  "type": "access"
}
```

| Claim | Description |
|-------|-------------|
| `sub` | Username (subject) |
| `exp` | Expiration timestamp (Unix epoch) |
| `type` | Token type: `access` or `refresh` |

### Token lifetimes

| Token Type | Default Lifetime |
|------------|------------------|
| Access Token | 60 minutes |
| Refresh Token | 30 days |

---

## Using authentication with other endpoints

When authentication is enabled, include the access token in the `Authorization` header:

```bash
curl -X GET http://localhost:8000/api/process/processes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### WebSocket authentication

For WebSocket connections, pass the token as a query parameter:

```
ws://localhost:8000/ws/status?token=eyJhbGciOiJIUzI1NiIs...
```

---

## Error handling

### Common error responses

| Status | Error | Description |
|--------|-------|-------------|
| 401 | `Unauthorized` | Missing or invalid token |
| 401 | `Token expired` | Access token has expired |
| 403 | `Forbidden` | User account is disabled |
| 422 | `Validation Error` | Invalid request body |

### Token refresh flow

When receiving a 401 response:

1. Send the refresh token to `POST /api/auth/refresh`
2. If successful, retry the original request with the new access token
3. If refresh fails, redirect the user to login

---

## Related pages

- [Authentication Feature Guide](../features/authentication.md)
- [WebSocket API](websocket.md)
- [Process Management API](process.md)
