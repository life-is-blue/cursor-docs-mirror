# Network, proxy, and remote connections

Fixes for connection issues when using Cursor behind a firewall, proxy, VPN, or over SSH.

## How do I run network diagnostics?

Go to **Cursor Settings** > **Network** and click **Run Diagnostics**. This tests your connection to Cursor's servers and identifies issues affecting AI features or updates.

## What if AI features stop working behind a proxy?

Cursor uses HTTP/2 for streaming responses. Some corporate proxies (like Zscaler) block HTTP/2.

Go to **Cursor Settings** > **Network** and set **HTTP Compatibility Mode** to **HTTP/1.1**, then restart Cursor.

## Which domains does Cursor need access to?

If your firewall blocks outbound connections, allowlist these domains:

- `*.cursor.sh` (includes `authenticate.cursor.sh` and `authenticator.cursor.sh`)
- `*.cursor-cdn.com`
- `*.cursorapi.com` (includes `marketplace.cursorapi.com`)

See the [network configuration docs](https://cursor.com/docs/enterprise/network-configuration.md) for the full list and connectivity tests.

## What if AI features don't work over SSH or remote connections?

When using Cursor's Remote SSH extension, AI features run on your local machine and communicate with the remote server for file access. If AI features stop working:

1. Check your local internet connection. AI requests go from your local machine to Cursor's servers, not from the remote host.
2. Verify the remote server isn't running out of memory or CPU. Resource exhaustion on the remote host can cause the connection to drop.
3. If your SSH connection drops frequently, increase the SSH keep-alive interval in your SSH config:
   ```
   Host your-server
     ServerAliveInterval 60
     ServerAliveCountMax 3
   ```
4. Restart Cursor after reconnecting. A dropped SSH session can leave stale processes.

## What if a VPN causes DNS resolution failures?

Cursor can inherit DNS settings from a previously active VPN. If AI features or agents fail with DNS errors after disconnecting a VPN:

1. Fully restart Cursor (not just reload the window). This clears inherited environment variables.
2. If the issue persists, check if your system's DNS has reverted to your normal resolver. On macOS, run `scutil --dns` in a terminal. On Linux, check `/etc/resolv.conf`.

## What does the "suspicious activity" message mean?

This message appears when your request is blocked as a security measure. VPNs can sometimes trigger it.

Try turning off your VPN first. If that doesn't help:

- Start a new chat
- Wait a few minutes and try again
- Sign in with a different authentication method (Google or GitHub)

## Related

- [Network configuration](https://cursor.com/docs/enterprise/network-configuration.md)
- [Agent troubleshooting](https://cursor.com/help/troubleshooting/agent-issues.md)
- [Performance](https://cursor.com/help/troubleshooting/performance.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
