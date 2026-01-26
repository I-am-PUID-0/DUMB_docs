---
title: Authentication FAQ
icon: lucide/key
---

# Authentication FAQ

Common questions and troubleshooting for DUMB's authentication system.

---

## Setup and configuration

### Do I need to enable authentication?

Authentication is optional. It's recommended if:

- DUMB is accessible from outside your local network
- Multiple users access the system
- You want to control who can start/stop services

You can skip authentication for local/trusted environments.

### How do I create the first user account?

When DUMB starts with no users:

1. Navigate to the DUMB frontend
2. You'll be redirected to `/setup`
3. Enter a username and password
4. Click **Create Account**

### Can I change my password?

Currently, password changes require:

1. Deleting the existing user
2. Creating a new user with the same username

!!! note "Future feature"

    Password change functionality may be added in future updates.

### How many users can I create?

There's no hard limit on the number of user accounts. Create as many as needed for your use case.

---

## Login issues

### "Invalid credentials" error

- **Check username** - Usernames are case-sensitive
- **Verify password** - Passwords are also case-sensitive
- **Account status** - Check if the user is disabled in Settings

### "User account is disabled" error

An administrator has disabled your account. Contact an admin to re-enable it via Settings :material-arrow-right: User Management.

### Session expires too quickly

Access tokens expire after 60 minutes by default. If you're experiencing frequent logouts:

- Check if **Remember Me** was selected during login
- Without Remember Me, tokens are stored in session storage and cleared when the browser closes
- With Remember Me, tokens persist in local storage

### Browser shows login page but I was logged in

- Your access token may have expired
- The frontend should automatically refresh - wait a moment
- If it persists, clear browser storage and log in again
- Check if authentication was recently disabled/re-enabled

---

## Account management

### How do I disable a user without deleting them?

1. Go to **Settings** :material-arrow-right: **User Management**
2. Find the user
3. Click the disable button

Disabled users cannot log in but their account remains for re-enabling later.

### "Cannot disable the last active user" error

DUMB prevents disabling or deleting the last non-disabled user to avoid lockouts. To disable this user:

1. Create another user account first
2. Then disable the original user

### How do I delete a user?

1. Go to **Settings** :material-arrow-right: **User Management**
2. Find the user
3. Click the delete button
4. Confirm the deletion

!!! warning "Permanent action"

    Deleted users cannot be recovered. Create a new account if needed.

---

## Lockout recovery

### I forgot my password - how do I reset it?

DUMB doesn't have a password reset feature. To recover access:

1. Stop the DUMB container
2. Edit `/config/users.json`
3. Set `"auth_enabled": false`
4. Start the container
5. Access DUMB and create a new user
6. Re-enable authentication

### I deleted all users and can't log in

Follow the lockout recovery steps above to disable authentication, then create a new user.

### The users.json file is corrupted

Replace it with a minimal valid file:

```json
{
  "version": 2,
  "jwt_secret": "",
  "auth_enabled": false,
  "setup_skipped": false,
  "users": []
}
```

Then restart DUMB and go through setup again. A new JWT secret will be generated automatically.

---

## API and tokens

### How long do tokens last?

| Token Type | Lifetime |
|------------|----------|
| Access Token | 60 minutes |
| Refresh Token | 30 days |

### How do I authenticate API requests?

Include the access token in the Authorization header:

```bash
curl -H "Authorization: Bearer <your_token>" http://localhost:8000/api/...
```

### How do I authenticate WebSocket connections?

Pass the token as a query parameter:

```
ws://localhost:8000/ws/status?token=<your_token>
```

### My API calls return 401 Unauthorized

- Verify the token is included in the Authorization header
- Check if the token has expired
- Ensure the format is `Bearer <token>` (with space)
- Try getting a new token via login

---

## Security

### Where are passwords stored?

Passwords are hashed using bcrypt and stored in `/config/users.json`. The original password is never stored.

### Is the JWT secret secure?

The JWT secret is auto-generated when the first user is created. It's stored in `/config/users.json` and should be kept confidential.

### Can I use DUMB without HTTPS?

Yes, but authentication tokens will be transmitted in plain text. For production deployments exposed to the internet:

- Use a reverse proxy with HTTPS
- Or deploy behind a VPN

### Should I disable authentication for local use?

For truly local/isolated environments (e.g., home lab with no internet exposure), disabling authentication simplifies access. However, if anyone on your network can reach DUMB, consider keeping authentication enabled.

---

## Related pages

- [Authentication Feature Guide](../features/authentication.md)
- [Authentication API](../api/auth.md)
- [DUMB FAQ](dumb.md)
