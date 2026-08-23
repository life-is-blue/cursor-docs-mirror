# Terminal integration

Cursor's AI works inside the terminal too. Generate commands with natural language, and let Agent run terminal commands as part of larger tasks.

## Can Agent run terminal commands on its own?

Yes. When Agent needs to install dependencies, run tests, or check build output, it runs terminal commands automatically based on your Run Mode settings.

Configure this in **Cursor Settings > Agents > Approvals & Execution**. In Cursor 3.6 and above, choose **Auto-review** (the default), **Allowlist**, or **Run Everything**:

- **Auto-review**. Allowlisted commands run, the rest run in the sandbox when possible, and anything else is screened by an LLM classifier that allows or blocks based on safety and how well the command matches your request. Blocked commands can be re-tried with your approval.
- **Allowlist**. Only commands on your allowlist run. With sandboxing enabled, supported commands outside the allowlist can run in the sandbox.
- **Run Everything**. All commands run without approval. Use **Auto-review** instead if you want most calls to run without prompting.

Before 3.5, the modes were **Run in Sandbox**, **Ask Every Time**, and **Run Everything**. **Ask Every Time** is deprecated in 3.5, and **Run in Sandbox** is now **Allowlist** with sandboxing enabled.

## What is the Cursor CLI?

The Cursor CLI brings Agent to your terminal as a standalone tool. It supports Agent, Plan, and Ask modes without opening the editor. Install it with:

```bash
curl https://cursor.com/install -fsS | bash
```

Learn more in the [CLI help article](https://cursor.com/help/integrations/cli.md) or at [cursor.com/cli](https://cursor.com/cli).

## Related

- [Terminal reference](https://cursor.com/docs/agent/tools/terminal.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
