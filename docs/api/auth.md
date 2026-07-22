---
title: Authentication API
icon: lucide/key
---

# Authentication API

The Authentication API provides endpoints for user management, login, token handling, and authentication configuration.

---

## Overview

Backend-native authentication endpoints are prefixed with `/auth`. Through the normal DUMB Frontend proxy, add `/api` (for example, `/api/auth/login`). When authentication is enabled, protected API endpoints require a valid JWT token in the `Authorization: Bearer <token>` header.

---

## Endpoints

### `GET /auth/status`

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

### `POST /auth/login`

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
| 401 | User account is disabled or the credentials are invalid |

#### Example

Directly against the backend from inside the DUMB container, or after intentionally publishing port `8000`:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

From the host in the standard deployment, use the DUMB Frontend proxy on the published port:

```bash
curl -X POST http://localhost:3005/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```

---

### `POST /auth/refresh`

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

### `POST /auth/verify`

Verifies that an access token is valid.

Pass the access token in the required `token` query parameter:

```text
POST /auth/verify?token=eyJhbGciOiJIUzI1NiIs...
```

#### Response

```json
{
  "valid": true,
  "username": "admin"
}
```

---

### `POST /auth/setup`

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
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Users already exist |
| 400 | Username is shorter than 3 characters or password is outside the 8–72 character range |

---

### `POST /auth/skip-setup`

Skips the initial setup wizard, leaving authentication disabled.

#### Response

```json
{
  "message": "Authentication setup skipped successfully"
}
```

---

### `POST /auth/enable`

Enables authentication. Requires at least one user to exist.

#### Response

```json
{
  "message": "Authentication enabled successfully"
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | No users exist - create a user first |

---

### `POST /auth/disable`

Disables authentication, allowing unauthenticated access to all endpoints.

!!! danger "Security warning"

    Disabling authentication exposes all DUMB functionality without any access control.

#### Response

```json
{
  "message": "Authentication disabled successfully"
}
```

---

## User management endpoints

These endpoints require authentication when auth is enabled.

### `GET /auth/users`

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

### `POST /auth/users`

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
  "username": "newuser",
  "disabled": false
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Username already exists |
| 400 | Username is shorter than 3 characters or password is outside the 8–72 character range |

---

### `PUT /auth/users/{username}`

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
  "username": "readonly",
  "disabled": true
}
```

#### Error responses

| Status | Description |
|--------|-------------|
| 400 | Cannot disable the last active user |
| 400 | User not found |

---

### `DELETE /auth/users/{username}`

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
| 400 | Cannot delete yourself, cannot delete the last user, or user not found |

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
curl -X GET http://localhost:3005/api/process/processes \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### WebSocket authentication

For WebSocket connections, pass the token as a query parameter:

```
ws://localhost:3005/ws/status?token=eyJhbGciOiJIUzI1NiIs...
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

1. Send the refresh token to `POST /auth/refresh` (or `/api/auth/refresh` through the frontend proxy)
2. If successful, retry the original request with the new access token
3. If refresh fails, redirect the user to login

---

## Related pages

- [Authentication Feature Guide](../features/authentication.md)
- [WebSocket API](websocket.md)
- [Process Management API](process.md)
