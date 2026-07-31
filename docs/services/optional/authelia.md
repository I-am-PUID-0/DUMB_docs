---
title: Authelia
description: Deploy and link a DUMB-managed Authelia identity provider for DUMB sign-in, Traefik Proxy Admin SSO, and selected Traefik ForwardAuth routes.
icon: lucide/shield
---

# Authelia

[Authelia](https://www.authelia.com/) is an identity and access-management
portal. DUMB can install and manage one Authelia instance, use it as an OpenID
Connect (OIDC) provider for DUMB and Traefik Proxy Admin (TPA), and publish a
reusable Traefik ForwardAuth middleware for selected application routes.

Authelia is optional. You can instead connect DUMB authentication to an
external Authelia deployment or another standards-compatible OIDC provider.

## What DUMB manages

| Item | DUMB behavior |
| --- | --- |
| Runtime | Downloads the official Linux release for AMD64, ARM64, or ARM and verifies its SHA-256 checksum |
| Database | Enables DUMB PostgreSQL and creates database `authelia` |
| Configuration | Generates `/config/authelia/configuration.yml` and validates it before start |
| Users | Stores bcrypt hashes in `/config/authelia/users_database.yml`; plaintext bootstrap passwords are not persisted |
| Secrets | Generates private session, storage-encryption, reset-password, OIDC HMAC, and RSA signing secrets under `/config/authelia/secrets` |
| OIDC clients | Creates separate credentials for DUMB and TPA instead of sharing one client |
| Notifications | Supports filesystem notification output for setup/labs or SMTP for production |
| Updates | Uses normal DUMB manual/scheduled release-update controls; auto-update defaults off |

!!! danger "Back up the complete Authelia config directory"
    Back up `/config/authelia`, especially its storage encryption key and OIDC
    signing material. PostgreSQL alone is not a complete backup. Losing the
    encryption key can make encrypted database values unrecoverable.

## Requirements

- A dedicated browser-reachable HTTPS hostname, such as
  `https://auth.example.com`.
- A cookie domain that equals or is a parent of that hostname, such as
  `example.com`.
- DNS and Traefik routing for the Authelia hostname.
- PostgreSQL storage; DUMB enables and initializes it automatically.
- SMTP for production password-reset and second-factor enrollment messages.
  The filesystem notifier is useful for initial testing but writes messages to
  `/config/authelia/notification.txt`.

Authelia requires an identity-verification message before the first TOTP device
can be enrolled, but that does not force you to configure an email provider for
initial setup. The filesystem notifier supplies the same one-time code through
the managed notification file. Use SMTP when users need to receive enrollment
and recovery messages without access to DUMB's local management interface.

Authelia's session cookie configuration requires a normal HTTPS hostname. Do
not use `localhost`, a bare IP address, or a public suffix as the cookie domain.

## Plan the addresses

The wizard asks only for browser-facing addresses. DUMB supplies internal
loopback addresses, callback paths, client IDs, and generated client secrets.

| Wizard value | Example | When it is needed |
| --- | --- | --- |
| TPA root domain | `example.com` | Offered from existing TPA domains when TPA is enabled |
| Authelia public URL | `https://auth.example.com` | Required in step 1 |
| Cookie domain | `example.com` | Required in step 1; normally the selected TPA root domain |
| DUMB public URL | `https://dumb.example.com` | Only when enabling Authelia sign-in for DUMB in step 2 |
| TPA public URL | `https://proxy.example.com` | Only when enabling Authelia admin sign-in for TPA in step 3 |
| Internal Authelia target | `http://127.0.0.1:9091` | DUMB/Traefik-managed; do not enter this as a public URL |

Do not enter a DUMB embedded path such as `/ui/authelia`, an internal service
port, or `localhost` in a public URL field.

## Guided setup

The frontend shows Authelia in onboarding and mounts the managed service-page
wizard only when the connected backend advertises the
`authelia_integration` capability. On an older backend, Authelia is omitted
from onboarding and any manually retained Authelia service entry keeps its
normal service controls without calling unsupported integration endpoints.

1. Enable **Authelia** from onboarding's Optional Services step or its DUMB
   service configuration.

    Onboarding installs Authelia and enables PostgreSQL, but intentionally does
    not start Authelia. A **Stopped** or **Unhealthy** status immediately after
    onboarding is expected and does not mean installation failed.

2. Open the **Authelia** service page and use
   **Set up this DUMB-managed Authelia instance**.
3. Complete **Step 1: Configure and start Authelia**. This is the only required
   wizard step. When TPA is enabled, DUMB checks its existing domains and offers
   them in the bootstrap form. Selecting `example.com` prefills
   `https://auth.example.com` and the `example.com` cookie domain. Manual entry
   remains available for external routing or a domain not managed by TPA.
4. Leave **Create or reuse this route in TPA after bootstrap** selected to
   publish the [Authelia portal route](#publish-the-authelia-portal)
   automatically, or create the route manually. Confirm its public HTTPS URL
   opens before configuring sign-in.
5. Choose any optional integrations:

   - **Step 2: DUMB sign-in** appears when the backend advertises `auth_oidc`
     and creates a dedicated DUMB OIDC client. **SSO + local fallback** is
     offered only with `auth_hybrid`; keep it until sign-in is tested. When the
     connected TPA release advertises DUMB application-route support, the same
     step first creates or verifies the prerequisite Authelia portal route, then
     creates or reuses the DUMB frontend's public route.
   - **Step 3: TPA admin sign-in** creates a separate TPA OIDC client. Skip it
     when TPA is not installed. A compatible TPA release also lets this step
     create or reuse TPA's own public route before configuring admin SSO.
   - **Step 4: ForwardAuth** creates a reusable middleware for selected apps
     that do not have their own OIDC login.

### Enroll the first authenticator

When Step 1 uses the recommended **Two factor** policy, the expanded walkthrough
includes **First login — enroll your authenticator**. Complete Step 2 before
starting this flow so Authelia can return to DUMB after authentication.

1. Keep the existing signed-in DUMB tab open.
2. Open DUMB in another tab and choose **Continue with Authelia**.
3. Enter the Authelia username and password created in Step 1.
4. In Authelia, open **Settings**. Under **One-Time Password**, choose **Add**.
   If Authelia instead shows **Register device** during sign-in, that link opens
   the same enrollment flow.
5. Return to the original DUMB tab. In the **Filesystem verification code** box
   immediately below the enrollment steps, choose
   **Reveal latest verification code**.
6. Enter the code DUMB displays into Authelia's **One-Time Code** field. For
   SMTP, retrieve the code from the user's email instead.
7. Scan Authelia's QR code with an authenticator app, enter the generated TOTP,
   and finish sign-in. The original login tab should redirect back to DUMB.

The filesystem helper deliberately requires authentication to be enabled and a
valid signed-in DUMB session. It reads only the fixed
`/config/authelia/notification.txt` file, returns only the newest delimited
verification code, uses `Cache-Control: no-store`, and never returns the
recipient, full notification, or revocation link. dmbdb keeps the revealed code
only in component memory and clears it after 60 seconds or when the walkthrough
is collapsed. If DUMB authentication is disabled, read the managed file from
the container instead; DUMB will not expose the code through an unauthenticated
API.

If the code is rejected, return to **Settings → One-Time Password → Add** and
reveal the newest code. A previously generated code may have expired or been
superseded.

DUMB renders and validates the configuration before the first start. It also
creates OIDC clients and transfers their generated secrets; no manual Authelia
client configuration is required. Adding the first or changing a managed OIDC
client performs a real Authelia stop/start so the provider and discovery
endpoints are loaded before the consuming application is enabled.

The entire walkthrough can be collapsed at any time, including before Step 1
is complete, so the normal service tabs and configuration editor remain
available. Before bootstrap it becomes an **Authelia setup is not complete**
summary with an **Open Authelia setup** button. After Step 1 succeeds it
automatically collapses to **Authelia bootstrap complete**; select
**Open setup & integrations** to return to Steps 2–4 or revise the managed
setup.

## Open the Authelia portal

After bootstrap starts Authelia, the Authelia service page offers **Open
Authelia Portal** in its integration summary and **Embedded UI** tab. The button
opens the configured public HTTPS address, such as
`https://auth.example.com`, in a top-level browser tab.

Authelia intentionally protects its password, account, and 2FA screens with
anti-framing headers. DUMB does not strip or weaken those controls, so Authelia
is launched instead of rendered inside an iframe. This protects the identity
provider from clickjacking and also keeps its session cookie on the correct
public origin.

Do not use a `/ui/authelia` address in bootstrap or OIDC fields. DUMB and TPA
OIDC discovery, authorization redirects, and normal user sign-in all use the
dedicated public HTTPS URL. The Authelia route must remain reachable and must
not have ForwardAuth, TPA Service SSO, or another login middleware attached to
it.

## Publish the Authelia portal

Authelia must have its own HTTPS route before browser login works. If an
existing TPA domain is selected during bootstrap, DUMB can create or reuse the
route automatically:

| TPA field | Value |
| --- | --- |
| Hostname | The hostname from **Authelia public URL** |
| Target host | `127.0.0.1` |
| Target port | The configured Authelia port; default `9091` |
| Target HTTPS | Off; Traefik terminates browser TLS |
| Authentication middleware | None |

Do not protect the Authelia portal with its own ForwardAuth middleware.

The automatic action is deliberately narrow. It inherits the selected TPA
domain's existing TLS/certificate configuration without changing it, targets
only DUMB's loopback Authelia listener, and adds no authentication middleware.
If another TPA service already owns the requested hostname, DUMB reports the
conflict and leaves that service unchanged. Authelia remains running, so you can
choose another hostname or resolve the TPA route manually.

After bootstrap, the completed setup summary retains a **Create/reuse Authelia
route** action. Use it when TPA was unavailable during bootstrap or when the
route was skipped. Step 2 also performs this prerequisite check before linking
DUMB authentication, because OIDC discovery cannot succeed until the public
Authelia issuer route is reachable.

The optional route controls in Steps 2 and 3 use the same safety model:

| Application | Default public hostname | Loopback target | TPA service authentication |
| --- | --- | --- | --- |
| DUMB frontend | `dumb.example.com` | DUMB frontend port; default `3005` | None; DUMB enforces its own login |
| TPA admin UI | `proxy.example.com` | TPA port; default `3004` | None; TPA enforces its own admin login |

The controls appear only when TPA advertises support for the requested route
application. This prevents an updated DUMB frontend from asking an older TPA
release to create a route using the legacy Authelia-only contract.

In a normal DUMB deployment, the DUMB frontend route targets
`127.0.0.1:3005`. During development, dmbdb may run in a separate devcontainer
while `dumb.frontend.enabled` is false. In that topology the wizard asks for a
frontend target host and port instead of requiring the managed frontend. Enter
an address reachable from the Traefik process in `dumb_dev`. A container name
such as `dmbdb_dev` works only when both containers share a user-defined Docker
network that provides container-name DNS; otherwise use a reachable container
IP for temporary testing or configure a shared development network. The wizard
rejects schemes and paths in this field.

Nuxt's development server requests virtual modules through paths containing an
encoded slash (`%2F`). Traefik 3.6.4 through 3.6.6 rejects these paths by default
with an empty HTTP 400 response. DUMB's generated Traefik entrypoint explicitly
allows encoded slashes while leaving the other encoded reserved characters at
Traefik's secure defaults. Restart DUMB after updating so the static Traefik
configuration is regenerated and the Traefik process is restarted. This setting
is needed for a public route targeting the dmbdb development server; production
dmbdb builds normally serve compiled asset paths that do not use Vite virtual
module URLs.

If Cloudflare Tunnel terminates public TLS, route traffic to DUMB Traefik as
described in the [Cloudflared guide](cloudflared.md). The browser-facing
Authelia URL must still use HTTPS.

## DUMB sign-in modes

| Mode | Behavior | Recommended use |
| --- | --- | --- |
| Local | Existing DUMB usernames/passwords only | Isolated or simple deployments |
| Hybrid | OIDC button plus local accounts | Default SSO rollout and break-glass recovery |
| OIDC only | OIDC button; local login disabled | Only after a successful SSO test and recovery planning |

DUMB uses Authorization Code with PKCE and validates state, nonce, issuer,
audience, signature, expiry, and the provider's JWKS. The callback creates a
short-lived, one-time exchange code; DUMB access and refresh tokens are not
placed in callback query strings.

The managed callback is:

```text
https://<dumb-public-host>/api/auth/oidc/callback
```

OIDC identities have the same DUMB privileges as local users. DUMB does not
currently have viewer/editor/admin role separation. An optional allowed-groups
list can deny sign-in unless the provider returns at least one matching group.

## DUMB-managed, external, or other OIDC providers

Open **DUMB Settings → Authentication → Sign-in provider** and select:

- **DUMB-managed Authelia** when this service has completed bootstrap. DUMB
  prefills its public issuer and `dumb` client ID, then creates or reuses the
  generated client when you select **Link managed Authelia**.
- **External Authelia** for an independently managed Authelia deployment.
- A named preset for Google, Authentik, Keycloak, Microsoft Entra ID, Auth0,
  Okta, ZITADEL, or Dex.
- **Custom / Generic OIDC** for another compatible provider.

External providers require a provider-side web application and the exact DUMB
redirect URI, public issuer URL, client ID, and client secret. Discovery
normally comes from:

```text
https://<issuer>/.well-known/openid-configuration
```

The DUMB redirect URI must use its browser-facing HTTPS FQDN. `localhost`, IP
addresses, single-label hostnames, HTTP, and embedded `/ui/...` routes are not
accepted.

Private/reserved provider addresses and plain HTTP are blocked unless you
explicitly enable the corresponding advanced option. Keep TLS verification on
whenever possible.

The managed TPA link uses Authelia's public HTTPS token and userinfo endpoints
so Authelia can enforce one consistent issuer across browser authorization and
server-side code exchange. DUMB does not rewrite endpoints supplied for
external Authelia or generic OIDC providers. HTTPS endpoints must present
certificates trusted by the DUMB or TPA process that connects to them; an
endpoint allowlist is not a TLS-verification bypass.

## OIDC versus ForwardAuth

- Use **OIDC** for DUMB or TPA sign-in. The application creates its own session
  and can apply provider group mappings.
- Use **ForwardAuth** when Traefik should gate an application that does not have
  suitable OIDC support.
- Do not attach both Authelia ForwardAuth and TPA Service SSO to the same
  router. That creates two login/session layers and confusing redirects.
- Do not automatically protect the DUMB hostname with ForwardAuth. First prove
  native DUMB OIDC works and retain a recovery route.

After step 4, TPA discovers:

```text
dumb-authelia-forward-auth@file
```

Attach it only to the TPA services you intend to protect.

## Files and ports

| Item | Location |
| --- | --- |
| Authelia portal | TCP `9091` |
| Generated config | `/config/authelia/configuration.yml` |
| File users | `/config/authelia/users_database.yml` |
| Generated secrets and signing key | `/config/authelia/secrets/` |
| DUMB-managed OIDC client state | `/config/authelia/dumb-managed.json` |
| Filesystem notifications | `/config/authelia/notification.txt` |
| Binary and version marker | `/authelia/` |
| Logs | `/log/authelia.log` |
| ForwardAuth middleware file | `/config/traefik/dynamic/authelia.yml` |

## Integration API

Backend-native routes use `/integrations/authelia`; through the normal DUMB
Frontend proxy use `/api/integrations/authelia`.

| Method and route | Purpose |
| --- | --- |
| `GET /integrations/authelia/status` | Return redacted managed, DUMB auth, TPA, and ForwardAuth state |
| `GET /integrations/authelia/verification-code` | Return only the newest filesystem-delivered identity-verification code; requires an authenticated DUMB session and is never available for SMTP |
| `GET /integrations/authelia/tpa-domains` | Return safe existing TPA domain choices, supported managed-route applications, and sanitized public routes for service-page links |
| `POST /integrations/authelia/tpa-route` | Create or reuse an unprotected TPA route for Authelia, DUMB, or TPA itself |
| `POST /integrations/authelia/bootstrap` | Save managed settings, create/update the bootstrap user, render configuration, and optionally start Authelia |
| `POST /integrations/authelia/link-dumb` | Create or accept an OIDC client and configure DUMB hybrid/OIDC auth |
| `POST /integrations/authelia/link-tpa` | Create the TPA client and call TPA's token-authenticated managed-provider linker |
| `POST /integrations/authelia/forward-auth` | Publish the managed or external Authelia file-provider middleware |

These routes use DUMB's normal authentication policy. Responses do not return
generated client secrets, user passwords, database credentials, or Authelia
secret material.

## Recovery

If OIDC is misconfigured:

1. Use **Use local account** on DUMB or TPA when hybrid/local fallback is
   enabled.
2. Correct the provider URL, client redirect URI, or group mapping.
3. Re-run the managed link step to update or rotate the client.
4. Restart Authelia after configuration changes and restart TPA when its
   provider environment changes.

If Authelia accepts the password and 2FA but TPA returns
`token_exchange_failed` with `invalid_request`, update TPA and run
**Link and restart TPA** again. The managed Authelia client requires
`client_secret_basic`; relinking records that method without exposing or
manually copying the generated client secret.

If OIDC-only mode caused a DUMB lockout, edit `/config/users.json` from the
container host and restore `"mode": "hybrid"` or `"mode": "local"`, then
restart DUMB. Protect that file: it contains DUMB's JWT and OIDC client
secrets.

## Related resources

- [DUMB authentication](../../features/authentication.md)
- [Authentication API](../../api/auth.md)
- [Traefik Proxy Admin](traefik-proxy-admin.md)
- [Authelia Traefik integration](https://www.authelia.com/integration/proxies/traefik/)
- [Authelia one-time password enrollment](https://www.authelia.com/overview/authentication/one-time-password/)
- [Authelia notification providers](https://www.authelia.com/configuration/notifications/introduction/)
- [Authelia OIDC provider](https://www.authelia.com/configuration/identity-providers/openid-connect/provider/)
- [Authelia session configuration](https://www.authelia.com/configuration/session/introduction/)
