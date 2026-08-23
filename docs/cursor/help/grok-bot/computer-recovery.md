# Recover Grok Bot computer data

What happens to the agent and sandbox data after accidental deletion, and how can they be recovered?

## What happens to my agent and computer data if I run `rm -rf *` inside the box?

Your agent conversation history is stored separately from the box, so running `rm -rf` inside the box does not delete it.

Grok Bot also keeps a durable copy of synced box data on the server. Reopening the box restores from that copy, so in most cases your agent conversations and synced box state come back even after local files inside the box are deleted.

If the box is still empty after these steps, avoid making further changes inside the box and [contact support](https://cursor.com/help/grok-bot/get-help.md) with your account email and what you were doing when the data disappeared, and we can investigate.

Files that live only on your local machine outside the sandbox are not covered by this recovery. Keep your own backups for local-only data.

## How do I reopen or reset my Grok Bot computer?

1. Update the desktop app to the latest version. Updating resolves many recovery failures.
2. Fully quit Grok Bot (not just close the window), then reopen it.
3. Open the agent whose computer you want to recover and use the computer controls to reopen the box.
4. Give it time to finish. Rehydration can take a while, so avoid repeatedly resetting or force-quitting, which can interrupt recovery or drop an unsynced thread.

Reset rebuilds the box from scratch. Use it only as a last resort, since anything not yet synced to the server will not come back.

If the box is still empty after these steps, avoid making further changes inside the box, and contact support with your account email and what you were doing when the data disappeared. We can investigate.

## What data can Grok Bot recover after accidental deletion?

| Data type                                  | Recoverable?                            |
| ------------------------------------------ | --------------------------------------- |
| Agent conversation history                 | Yes. Stored outside the box filesystem. |
| Sandbox files synced to the durable store  | Yes. Rehydrated on reopen or reset.     |
| Local files on your Mac or Windows machine | No. Use your own backups.               |

## Related

- [Getting started with Grok Bot](https://cursor.com/help/grok-bot/getting-started.md)
- [Store secrets securely](https://cursor.com/help/grok-bot/secrets.md)
- [Get help](https://cursor.com/help/grok-bot/get-help.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
