# How do I troubleshoot Tab completions?

Troubleshooting steps for when Tab completions stop appearing or behave unexpectedly.

## Why aren't Tab suggestions appearing?

1. **Plan limits**: Free (Hobby) users have a monthly Tab allowance. Once it's used up, suggestions pause until the next billing cycle.
2. **HTTP compatibility**: Some networks block HTTP/2. Go to **Cursor Settings** > search "HTTP Compatibility Mode" > enable it to fall back to HTTP/1.1, then restart Cursor.
3. **Outdated version**: Press **Cmd/Ctrl+Shift+P** > "Cursor: Attempt Update" to check for updates.
4. **No internet**: Tab requires a connection to work.

## How can I improve Tab suggestion quality?

Tab builds context from your recent edits and the code around your cursor. A new or empty file gives it less to work with.

- Make a few manual edits first to signal your intent
- Check for conflicting extensions (see [Extension conflicts](https://cursor.com/help/troubleshooting/extensions.md))

## What if Tab feels slow?

- Check your internet connection speed
- Disable extensions you're not using
- VPNs and proxies can add latency

## How do I toggle Tab off for certain file types?

Click the **Tab** status indicator in the bottom-right corner of Cursor. From there you can disable Tab for specific file extensions (like markdown or JSON).

## Related

- [Tab completion](https://cursor.com/help/ai-features/tab.md)
- [Extension conflicts](https://cursor.com/help/troubleshooting/extensions.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
