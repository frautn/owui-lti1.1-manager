# owui-lti1.1-manager
Django manager for owui-lti1.1. Project owui-lti1.1 is a middleware that exposes Open WebUI as an LTI external tool. This project, owui-lti1.1-manager, is an LTI for managing knowledge bases and workspaces in that Open WebUI server.

## LTI 1.1 Launch Support

This app now accepts an LTI 1.1 launch from Moodle, verifies the OAuth 1.0 signature,
auto-signs in a Django user, and shows launch data on the homepage.

### Endpoints

- `POST /lti/launch/`: LTI launch URL to configure in Moodle.
- `GET /`: Homepage shown after successful launch.

### Required Environment Variables

- `LTI_CONSUMERS`: consumer key/secret map in this format:
	`key1:secret1,key2:secret2`
- `ALLOWED_HOSTS` (recommended):
	`localhost,127.0.0.1,your-domain.example`

Example:

```bash
export LTI_CONSUMERS="moodle_key:moodle_shared_secret"
export ALLOWED_HOSTS="localhost,127.0.0.1"
```

### Moodle Tool Configuration

- Launch URL: `https://your-domain/lti/launch/`
- Consumer key: same key used in `LTI_CONSUMERS`
- Shared secret: same secret used in `LTI_CONSUMERS`

After launch, the Django app stores the launch payload in session and renders it on `/`.
