# What are coding agents?

A coding agent is an AI system that writes and changes software on its own. You describe a goal in plain language, and the agent plans the work, edits files, runs commands, and checks its own results.

## What is an AI coding agent?

An AI coding agent uses large language models (LLMs) to build software and accomplish tasks for you. It runs [tools in a loop](https://cursor.com/learn/agents.md): instead of always returning a single answer, it works through a series of tool calls, deciding what to do next based on the result of each action. You set the goal and review the output. Cursor built one of the first coding agents in late 2024, and agents have now become the main way people write software.

The quality of the output depends on the model, the [harness](https://cursor.com/learn/working-with-agents.md), and the context you provide. Cursor works with every [frontier model](https://cursor.com/docs/models-and-pricing.md) and tunes its harness to each one to get the most out of every model when building software. You can compare model results on the [CursorBench page](/cursorbench).

## What is inside a coding agent?

A coding agent combines three parts:

1. **The model** does the reasoning and decides what to do next.
2. **Tools** let it act, like reading and editing files, searching the codebase, and running the terminal.
3. **The harness** contains the system instructions, the context you provide, and the [tool definitions](/blog/dynamic-context-discovery) that turn raw model output into useful work.

## How do coding agents use tools?

Tools are what let a model act on the world instead of only describing it. A coding agent can [search your codebase](https://cursor.com/docs/agent/tools/search.md), read and edit files, run shell commands, browse the web, and [record a demo](/blog/agent-computer-use) of what it built. Each [tool call](https://cursor.com/learn/tool-calling.md) returns a result the agent reads before deciding its next move.

## How are coding agents different from autocomplete?

AI autocomplete, like Cursor's [Tab](https://cursor.com/help/ai-features/tab.md) model, suggests the next line or action as you type. A coding agent, in contrast, takes an entire task and carries it out across many files in your codebase. Most people now build software with coding agents.

## How do I use coding agents in Cursor?

Cursor is a coding agent for building ambitious software. Open [Agent mode](https://cursor.com/help/ai-features/agent.md) and describe what you want, and the agent explores your codebase, makes changes, and verifies them. Your agents can run locally, or you can hand them off to the [cloud](https://cursor.com/help/ai-features/cloud-agents.md) to keep working after you close your laptop. You can use Cursor from the web at [cursor.com/agents](https://cursor.com/agents), on mobile, or programmatically through our [SDK](https://cursor.com/docs/sdk/typescript.md).

## What are some other coding agents?

Coding agents are a growing category. Other examples include Claude Code and OpenAI Codex, which run on Anthropic and OpenAI models. Cursor works with those same frontier models and many more, so you can route each task to the model that fits it. Cursor also meets you across the desktop, terminal, web, and mobile.

## Related

- [Agent mode](https://cursor.com/help/ai-features/agent.md)
- [What is agentic coding?](https://cursor.com/help/ai-features/agentic-coding.md)
- [What are background agents?](https://cursor.com/help/ai-features/background-agents.md)
- [Agents (Cursor Learn)](https://cursor.com/learn/agents.md)
- [Agent reference](https://cursor.com/docs/agent/overview.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
