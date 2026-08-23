# How do I build an AI coding agent?

You can build a coding agent from three parts: a model, a set of tools, and a harness that runs them in a loop. While you can write it yourself to better understand how agents work, we recommend using the [Cursor SDK](https://cursor.com/docs/sdk/typescript.md) to build on the same runtime that powers Cursor.

## What is a coding agent made of?

Every coding agent needs a harness, which combines the model the user selects, the tools the agent can access, and the instructions the user provides to achieve a goal. From there, the agent works autonomously, using those tools to read and write files, search the code, or look up information on the web to create working software. Learn the building blocks in [Cursor Learn](https://cursor.com/learn/agents.md).

## Can I build an agent without coding?

Yes. If you want to automate work or repeat a workflow without managing code, use [Automations](https://cursor.com/help/ai-features/automations.md). You pick a model, provide instructions, and run your agent on a schedule or from events in GitHub, Slack, Linear, and more.

For example, Cursor's security team built a fleet of [security agents](/blog/security-agents) with Automations that review more than 3,000 internal PRs a week and catch over 200 vulnerabilities.

## How do I build a coding agent with the Cursor SDK?

The [Cursor SDK](https://cursor.com/docs/sdk/typescript.md) lets you launch agents with the same harness, runtime, and models that power Cursor. Install it, create an agent, send it a prompt, and stream the results. You build custom workflows on top of Cursor's agent instead of rebuilding the agent stack yourself.

```ts
import { Agent } from "@cursor/sdk";

const agent = await Agent.create({
  apiKey: process.env.CURSOR_API_KEY,
  model: { id: "composer-2.5" },
  local: { cwd: process.cwd() },
});

const run = await agent.send("Summarize what this repository does");

for await (const event of run.stream()) {
  console.log(event);
}
```

## What can I build with the Cursor SDK?

You can run agents on your machine or on Cursor's cloud against a dedicated VM, with any frontier model. Teams kick off agents from CI/CD to summarize changes and fix failures, build internal tools, and embed an agent experience inside their own products. See the [TypeScript](https://cursor.com/docs/sdk/typescript.md) and [Python](https://cursor.com/docs/sdk/python.md) SDK docs to start, the [SDK Bridge](https://cursor.com/docs/sdk/bridge.md) for other languages, or explore our [cookbook of examples](https://github.com/cursor/cookbook).

## Related

- [Cursor SDK (TypeScript)](https://cursor.com/docs/sdk/typescript.md)
- [Cursor SDK (Python)](https://cursor.com/docs/sdk/python.md)
- [SDK Bridge](https://cursor.com/docs/sdk/bridge.md)
- [What are coding agents?](https://cursor.com/help/ai-features/coding-agents.md)
- [Automations](https://cursor.com/help/ai-features/automations.md)
- [Build programmatic agents with the Cursor SDK](/blog/typescript-sdk)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
