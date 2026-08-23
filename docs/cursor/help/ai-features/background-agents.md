# What are background agents?

Background agents are coding agents that typically run for a very long time. In practice, that means moving a task from your local device to the cloud, where the agent takes it from start to finish without interruption and reports back with proof that the work is done. In Cursor, we call these [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md).

These agents can build features, fix bugs, write tests, and automatically open pull requests when they finish.

## How do background agents work?

Each Cloud Agent runs on its own dedicated virtual machine with a full [development environment](https://cursor.com/docs/cloud-agent/setup.md): your repository, dependencies, secrets, and network access. It plans the task, edits code, runs commands, and [tests its work](https://cursor.com/docs/cloud-agent/capabilities.md) over minutes or hours. Because it runs remotely, you can close your laptop and check the result later.

The VM is sandboxed and isolated from your local machine, so the agent's commands never touch your environment. Cursor wraps each run in [secret redaction, network policies, and credential management](https://cursor.com/docs/cloud-agent/security-network.md), and you control which repositories, secrets, and network access an environment gets. We share more in [What we've learned building cloud agents](/blog/cloud-agent-lessons).

## How do background agents show their work?

Background agents produce artifacts to demo their changes. As an agent works, it tests its changes and attaches videos, screenshots, and logs to the pull request, so you can validate the work without checking out the branch. You can also take control of the agent's remote desktop to use the software it built and make edits yourself.

See the [announcement blog post](/blog/agent-computer-use) for real examples of agents demoing their work.

## How do I start a background agent?

- In Cursor, select **Cloud** by the agent input
- On the web or mobile, go to [cursor.com/agents](https://cursor.com/agents)
- In Slack, GitHub, or Linear, mention **@Cursor**

You can also run them on a schedule or from events with [Automations](https://cursor.com/help/ai-features/automations.md).

## Related

- [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md)
- [What is multi-agent coding?](https://cursor.com/help/ai-features/multi-agent.md)
- [Cloud Agent reference](https://cursor.com/docs/cloud-agent.md)
- [Cloud Agent capabilities](https://cursor.com/docs/cloud-agent/capabilities.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
