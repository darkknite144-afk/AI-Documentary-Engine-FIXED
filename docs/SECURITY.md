# Security

- Secrets only through environment variables / `.env` file.
- Never commit `.env` files.
- Never log API keys or full source content at DEBUG level in production.
- `.env.example` is the only env file tracked in version control.
