# Reporting a bug

Help us fix issues faster by including the right information in your bug report.

## What should I include in a bug report?

- **Cursor version**: Click **Cursor** > **About Cursor** in the menu bar
- **Operating system**: Mac, Windows, or Linux, plus the version
- **Steps to reproduce**: What you did before the issue happened
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What happened instead
- **Screenshots or screen recordings**: If the issue is visual
- **Request ID**: See below for how to find it
- **Console errors**: Go to **Help** > **Toggle Developer Tools** to check for errors

## Where do I report Cursor bugs?

Post on [forum.cursor.com](https://forum.cursor.com) for community help and visibility.

## What is a request ID?

A request ID is a unique identifier generated for each request you make to Cursor. It allows the support team to locate your specific request in internal systems and investigate what went wrong.

Request IDs are only meaningful within Cursor's backend. They're lookup keys with no value outside our systems, so you don't need to treat them as confidential.

## How do I find my request ID?

1. Open the relevant conversation in the Chat sidebar
2. Click the context menu ("..." menu)
3. Select **Copy Request ID**
4. Share this ID in the forum or email

## How does Privacy Mode affect debugging?

Your privacy settings affect what the support team can see when investigating your issue.

### With Privacy Mode enabled

The team can only see:

- Which model was used
- Whether tool failures occurred (but not which tools failed)
- Backend failures unrelated to your prompt, code, or agent actions

### With Share Data enabled

The team can see:

- The full conversation between you and the agent
- Tool calls, including details about which ones failed
- Context provided to the agent (system prompt, rules, git status)

For agent behavior issues, understanding what happened without Share Data is difficult. For connectivity issues, the team can often debug them with Privacy Mode enabled since these don't require seeing your code or conversation content.

Privacy Mode is per-request. Changing your privacy setting does not retroactively affect previous requests. Each request is logged according to the privacy mode in effect when it was submitted. If you encountered an issue while Privacy Mode was enabled, switching to Share Data afterward won't give the team visibility into that original request.

## How should I report an issue involving unexpected agent behavior?

1. Temporarily enable **Share Data** in your privacy settings
2. Reproduce the issue by performing the same actions that caused the problem
3. Copy the new Request ID using the context menu
4. Send the Request ID via the forum or email
5. Switch back to **Privacy Mode** if preferred

## Related

- [Privacy and data](https://cursor.com/help/security-and-privacy/privacy.md)
- [Installation and startup](https://cursor.com/help/troubleshooting/install-issues.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
