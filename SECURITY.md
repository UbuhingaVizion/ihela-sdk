# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in ihela-sdk, please report it to:

**Email**: info@ubuviz.com

Please do not report security vulnerabilities through public GitHub issues.

Include the following in your report:

- A description of the vulnerability
- Steps to reproduce the issue
- Affected versions
- Any potential mitigations you've identified

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Best Practices

- Never hardcode `client_id`, `client_secret`, or `pin_code` values in your code
- Use environment variables or a secrets manager for credentials
- The SDK automatically masks sensitive fields (`pin_code`, `access_token`, etc.) in debug logs
- Always use HTTPS for iHela API communication (enforced by default)
