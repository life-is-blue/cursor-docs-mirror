# What is multi-agent coding?

Multi-agent coding is running more than one AI agent at the same time, each working on a different task or a different slice of the same task. As models run longer and take on more, you move from guiding one agent to coordinating several.

## How do I run multiple agents in Cursor?

Use the [Agents Window](https://cursor.com/docs/agent/agents-window.md), Cursor's agent-first workspace for running and managing many agents across repositories and environments. You can launch parallel agents in the cloud, work with them from the web, mobile, Slack, GitHub, and Linear, and move a task between local and cloud with a click.

## What are subagents?

Subagents are agents that a main agent spawns to handle part of a task. Each runs in its own context window and returns a result to the main conversation, so work happens in parallel without crowding one context. Cursor includes built-in subagents for research, shell, and browser work, and you can define your own. See the [subagents reference](https://cursor.com/docs/subagents.md).

## How do I multitask with agents?

Type `/multitask` to have Cursor run async subagents in parallel instead of queuing your requests. From a plan, click **Build in Parallel** and Cursor runs independent steps at once while keeping dependent steps in order. This helps when tasks run long enough that waiting on each one in turn would slow you down.

## How do I manage many agents at once?

When a task runs for a long time, hand it to the cloud so you can close your laptop and switch context. Pull the changes back locally when you need to make edits yourself.

Inside the Agents Window, manage every agent from the sidebar and pin the chats you return to most so they stay at the top. Some engineers pin a long-running conversation and let the agent automatically summarize its own context to keep working over a long period.

As you switch between agents, artifacts like screenshots and demo videos help you review an agent's work and see whether the software runs, without stepping through every line of the diff to confirm the task is done.

## Related

- [Agents Window reference](https://cursor.com/docs/agent/agents-window.md)
- [Subagents reference](https://cursor.com/docs/subagents.md)
- [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md)
- [What are background agents?](https://cursor.com/help/ai-features/background-agents.md)
- [Towards self-driving codebases](/blog/self-driving-codebases)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
