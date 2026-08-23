# Cloud Agents

Cloud Agents run in isolated cloud environments instead of on your local machine.

## What can Cloud Agents do?

Cloud Agents handle coding tasks without you needing to be in the loop. They can build features, fix bugs, write tests, open PRs, and share a video of it working. Each task starts from a configured cloud environment with the repos, dependencies, secrets, and network access the agent needs.

Cloud Agents can also use multi-repo environments. This lets one agent work across frontend, backend, infrastructure, or shared-library repos in the same run.

## How does "Move to Cloud" handle my file state?

"Move to Cloud" does not snapshot your local uncommitted changes. The cloud agent starts from a clean git state on the remote repository. It transfers your conversation history and context, but not dirty files or uncommitted edits. Commit or stash your changes before moving a conversation to the cloud if you want the agent to work from your latest state.

## Can Cloud Agents test my app in a browser?

Yes. Each cloud agent runs in its own isolated VM with a full desktop environment. Agents use a mouse and keyboard to control the desktop and browser, the same way a human developer would.

This means agents can start dev servers, open the app in a browser, click through UI flows, and verify their changes work before pushing a PR.

## How do Cloud Agents show their work?

Agents attach screenshots, videos, and log references to the PR so you can validate changes without checking out the branch.

## Can Cloud Agents use MCP tools?

Yes. Add and manage MCP servers through the MCP dropdown at [cursor.com/agents](https://cursor.com/agents). This gives agents access to databases, APIs, and third-party services during their runs.

Cloud agents support HTTP and stdio servers, plus OAuth for servers that need it. See the [Cloud Agent capabilities page](https://cursor.com/docs/cloud-agent/capabilities.md) for setup details.

## Do Cloud Agents run hooks?

Yes. Cloud Agents run command-based hooks from `.cursor/hooks.json` in your repository. On Enterprise plans, they also run team hooks and enterprise-managed hooks.

Supported hooks include tool and file hooks (`beforeShellExecution`, `afterShellExecution`, `beforeReadFile`, `afterFileEdit`, `preToolUse`, `postToolUse`, `postToolUseFailure`) and conversation-level lifecycle hooks such as `beforeSubmitPrompt`, `afterAgentResponse`, `afterAgentThought`, `stop`, `subagentStart`, `subagentStop`, and `preCompact`.

Conversation-level hooks let you observe prompts, responses, and thinking; control subagents; react to compaction; and run logic when a turn completes. You can use them to build self-correcting loops around agent output and reasoning.

Hooks start once the agent has a writable environment. IDE-specific hooks like Tab hooks and `workspaceOpen` don't apply. `sessionEnd` doesn't apply because cloud agents have no editor-lifetime session boundary. Prompt-based hooks also aren't supported in cloud agents. User-level hooks from `~/.cursor/hooks.json` aren't loaded since the VM doesn't have access to your local configuration.

See the [full hooks support matrix](https://cursor.com/docs/hooks.md#cloud-agent-support) for details.

## Can Cloud Agents fix CI failures?

Yes. Cloud Agents automatically try to fix GitHub Actions failures on PRs they create. They ignore checks that are also failing on the base branch. This is currently available on Teams plans.

To disable this on a specific PR, comment `@cursor autofix off`. To re-enable it, comment `@cursor autofix on`. You can also disable it globally from [Cursor Dashboard > Cloud Agents > My Settings](https://cursor.com/dashboard/cloud-agents).

## What do I need to use Cloud Agents?

Cloud Agents are available on all paid Cursor plans.

## How do I set up Cloud Agents?

Create a new environment in your [Cloud Agents dashboard](https://cursor.com/dashboard/cloud-agents#environments). You'll connect your GitHub, GitLab, Azure DevOps, or Bitbucket Cloud account, select one or more repositories, add secrets or environment variables, and verify the setup. See the [full setup guide](https://cursor.com/docs/cloud-agent/setup.md) for multi-repo environments, environment-scoped secrets, network access, and Dockerfiles.

## How do I use the redesigned project and repo picker?

The project picker keeps common setup steps in one place. You can:

- Create a project without leaving the picker
- Connect GitHub, GitLab, or Azure DevOps inline
- Search projects scoped by location: **This Computer**, **Cloud**, or a remote machine
- Remove a project from **Recents** with one click

Remote Machines are consolidated in the same picker flow so you can open local, cloud, and remote work from one place.

## How do I start a Cloud Agent task?

- **In Cursor**: Select **Cloud** in the dropdown under the agent input
- **On the web**: Go to [cursor.com/agents](https://cursor.com/agents)
- **Via Slack**: Use **@Cursor**
- **On GitHub**: Comment **@cursor** on a PR or issue
- **On Bitbucket Cloud**: Comment **@cursor** on a PR
- **In Linear**: Use **@Cursor** on an issue
- **Via API**: Use the [Cloud Agent API](https://cursor.com/docs/cloud-agent/api/endpoints.md)

## How is Cloud Agent usage priced?

Cloud Agents are charged at [API pricing](https://cursor.com/docs/models-and-pricing.md#model-pricing) for the selected model. You can select the context window size for supported models. A larger context window can increase token usage and costs.

## Can I run Cloud Agents automatically or on a cron?

Yes. Use [Automations](https://cursor.com/help/ai-features/automations.md) to run Cloud Agents on a schedule or from events in GitHub, Slack, Linear, PagerDuty, or webhooks. Set them up at [cursor.com/automations](https://cursor.com/automations). See the [automations docs](https://cursor.com/docs/cloud-agent/automations.md) for trigger types and templates.

## Does Privacy Mode work with Cloud Agents?

Yes. Cloud Agents are available with Privacy Mode. See the [Cloud Agent security page](https://cursor.com/docs/cloud-agent/security-network.md) for details.

## Can Cloud Agents federate into AWS or other clouds without long-lived keys?

Yes. Cursor-managed Cloud Agent VMs can mint short-lived [OIDC JWTs](https://cursor.com/docs/cloud-agent/identity.md) from a local socket. Verifiers use Cursor's public discovery and JWKS endpoints to check the signature and authorize on claims such as `sub`, `team_id`, and `cloud_agent_id`.

## Can Cloud Agents read their own id, owner, or current turn from the VM?

Yes. Cursor-managed Cloud Agent VMs serve an [agent metadata](https://cursor.com/docs/cloud-agent/metadata.md) API on the same local socket as [OIDC tokens](https://cursor.com/docs/cloud-agent/identity.md). A `GET` of a path such as `/v1/meta-data/agent/id` returns the bare value as text.

## Related

- [Automations](https://cursor.com/help/ai-features/automations.md)
- [What are background agents?](https://cursor.com/help/ai-features/background-agents.md)
- [What is multi-agent coding?](https://cursor.com/help/ai-features/multi-agent.md)
- [Cloud Agent reference](https://cursor.com/docs/cloud-agent.md)
- [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities.md)
- [Cloud Agent setup](https://cursor.com/docs/cloud-agent/setup.md)
- [OIDC tokens](https://cursor.com/docs/cloud-agent/identity.md)
- [Agent metadata](https://cursor.com/docs/cloud-agent/metadata.md)
- [Automations](https://cursor.com/docs/cloud-agent/automations.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
