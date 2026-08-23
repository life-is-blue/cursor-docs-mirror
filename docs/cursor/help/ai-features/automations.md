# Automations

Cursor Automations run [Cloud Agents](https://cursor.com/docs/cloud-agent.md) in the background, either on a schedule or in response to events from GitHub, GitLab, Slack, webhooks, Linear, and more.

## What can Automations do?

Automations let you run Cloud Agents without manual input. Common uses include:

- Reviewing pull requests when they're opened
- Cleaning up feature flags on a schedule
- Triaging bugs from Slack messages
- Running security scans after CI completes

Browse templates in the [Automations marketplace](https://cursor.com/marketplace/automations) to get started.

## How do I create an automation?

Create a new automation in the [Agents Window](https://cursor.com/docs/agent/agents-window.md), at [cursor.com/automations/new](https://cursor.com/automations/new), or from a template in the [Cursor Marketplace](https://cursor.com/marketplace/automations).

1. Choose a trigger (e.g. every hour, when a PR is opened, or when a Slack message arrives)
2. Write a prompt telling the agent what to do
3. Select optional tools the agent can use (Comment on PR, Send to Slack, MCP, and more)
4. Choose whether the automation needs a repository, multiple repositories, or no repository at all
5. Save and activate the automation

The Automations page also includes three Cursor-managed agents:

- [Bugbot](https://cursor.com/docs/bugbot.md) reviews pull requests for bugs and code quality issues.
- [Security Agents](https://cursor.com/docs/security-agents.md) review pull requests and scan codebases for vulnerabilities.
- [PR Routing & Approval](https://cursor.com/docs/approval-agents.md) routes pull requests to reviewers and can approve low-risk changes.

## Can I create automations without connecting a repository?

Yes. Automations can run without any attached repos. These automations do not clone code. They work well for workflows that only use Slack, MCP, webhooks, Linear, or PagerDuty.

Repository settings control whether the agent has code access:

- **No repository**: The agent does not clone code. Use this for Slack, MCP, webhook, Linear, or PagerDuty workflows. It cannot edit code or open pull requests.
- **Single repository**: The agent works in one repository and branch. Use this when the automation should read, review, or change code in one codebase.
- **Multi-repo environment**: The agent works across the repositories in an environment. Use this when the task spans multiple codebases.

## Which triggers are available?

| Trigger                                        | Fires when                                          |
| ---------------------------------------------- | --------------------------------------------------- |
| **Scheduled**                                  | A recurring schedule or cron expression matches     |
| **Source control: Draft opened**               | A draft PR is created                               |
| **Source control: PR opened**                  | A non-draft PR is created or marked ready           |
| **Source control: PR pushed**                  | New commits are pushed to an existing PR            |
| **Source control: PR merged**                  | A PR is merged                                      |
| **Source control: Push to branch**             | Commits are pushed to a specific branch             |
| **GitHub, GitLab, or Bitbucket: PR commented** | Someone leaves a top-level comment on a PR          |
| **GitHub: CI completed**                       | A GitHub check finishes                             |
| **Slack: New message**                         | A message is sent to a connected public channel     |
| **Slack: Channel created**                     | A new public channel is created                     |
| **Linear: Issue created**                      | A new Linear issue is created                       |
| **Linear: Status changed**                     | An issue's status changes                           |
| **Linear: End of cycle**                       | A Linear cycle completes                            |
| **PagerDuty**                                  | An incident is triggered, acknowledged, or resolved |
| **Webhook**                                    | An HTTP POST is sent to the automation's endpoint   |

An automation can have more than one trigger. It runs when any of the triggers fire.

Source control triggers work with GitHub, GitLab, and Bitbucket Cloud. Provider support varies; GitHub supports the full set, and other providers support the core triggers plus a few extras. See the [automations reference](https://cursor.com/docs/cloud-agent/automations.md#source-control-triggers) for the per-provider breakdown.

## Which tools can automations use?

- **Comment on pull request**: Posts review comments, inline code comments, or approvals on a target PR
- **Request reviewers**: Assigns reviewers on a target PR
- **Send to Slack**: Sends messages to a Slack channel
- **Read Slack channels**: Gives read access to public Slack channels
- **MCP server**: Connects external tools and data sources via [MCP](https://cursor.com/docs/mcp.md)
- **Memories**: Stores and recalls persistent notes across runs as named entries (`MEMORIES.md` by default). Use with caution if your automation handles untrusted input; malicious inputs could write misleading memories that affect future runs.

## How are automations billed?

Automations create Cloud Agent runs. Each run is billed at [API pricing](https://cursor.com/docs/models-and-pricing.md#model-pricing) for the selected model.

## How do I control who can see my automation?

Choose a permission level when creating the automation:

- **Private**: Only you can manage it. Team admins can view and disable it.
- **Team Visible**: Team members can view it. Only you can manage it. Team admins can disable it.
- **Team Owned**: Team members can view it. Only team admins can manage it. Creating a team-owned automation requires team admin access.

## How do I write a good automation prompt?

- Be specific about what the agent should check, change, or produce
- Reference the tools you've enabled
- Include decision rules for different cases (e.g. "if the PR touches migrations, request a review from the database team")
- Set a quality bar for when the agent should act vs. do nothing

Browse the [Automations marketplace](https://cursor.com/marketplace/automations) for examples.

## Related

- [Agents Window](https://cursor.com/docs/agent/agents-window.md)
- [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md)
- [Automations reference](https://cursor.com/docs/cloud-agent/automations.md)
- [Cloud Agent setup](https://cursor.com/docs/cloud-agent/setup.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
