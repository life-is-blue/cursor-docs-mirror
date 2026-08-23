# Git

Cursor adds AI-powered git features on top of the standard Source Control panel.

## Can Agent write commit messages for me?

Yes. Stage your changes, then click the sparkle icon in the commit message input to generate a message based on your diff and repo history.

## How does AI merge conflict resolution work?

When you hit a merge conflict, click **Resolve in Chat** in the conflict UI. Agent analyzes both sides and proposes a resolution.

## How does Agent attribution work?

When Agent creates commits or pull requests, Cursor can add a `Made with Cursor` trailer automatically. This applies to both git commits and pull requests created via `gh pr create`.

Attribution is on by default. Toggle it in **Cursor Settings** > **Agent** > **Attribution**.

Starting in Cursor 3.11, this setting moves to **Cursor Settings** > **Git & PRs** > **Attribution**.

## Can enterprise admins control commit attribution?

Yes. Enterprise admins can globally disable commit attribution for all team members from the [Admin Dashboard](https://cursor.com/docs/account/teams/dashboard.md). This overrides individual user settings, so no trailers are appended to Agent commits or PRs across the organization.

Navigate to **Admin Dashboard > Settings** to toggle commit attribution on or off for your entire team.

## What is Cursor Blame?

Cursor Blame tracks which code was written by AI and which was written by humans. It annotates your git history so you can see at a glance whether a line was AI-generated. This helps with code review, auditing, and understanding your codebase's AI footprint.

See the [Cursor Blame reference](https://cursor.com/docs/integrations/cursor-blame.md) for setup and usage details.

## Does Agent work across multiple workspaces?

Yes. Each open workspace has its own independent Agent and git context. Agent in one window won't affect files in another workspace.

## Related

- [Cursor Blame](https://cursor.com/docs/integrations/cursor-blame.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
