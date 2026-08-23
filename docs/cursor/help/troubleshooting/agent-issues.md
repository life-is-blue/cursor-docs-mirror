# Agent troubleshooting

Fixes for common Agent issues with file access, rules, terminal commands, and more.

## How can I improve Agent accuracy?

- Be specific in your prompts: include expected behavior and constraints
- Use [Plan mode](https://cursor.com/help/ai-features/plan-mode.md) first for tasks that touch many files
- Start a new chat when you finish a feature or switch tasks
- Add [rules](https://cursor.com/help/customization/rules.md) in `.cursor/rules/` for patterns you want Agent to follow every time
- Type `@` followed by a file or folder name to give Agent targeted context

## What if Agent doesn't pick up my files?

1. Check your `.cursorignore` file in the project root. Files listed there are blocked from Agent, codebase search, and `@` mentions.
2. Check `.gitignore`. Patterns there can also prevent Agent from discovering files.
3. Reindex your project: open the command palette and search for "Reindex."
4. Attach files directly by typing `@` followed by the filename in the chat input.

## How do I undo Agent changes?

Hover over a previous message and click **Restore Checkpoint** in the bottom right to roll back all changes Agent made after that point.

Checkpoints are stored locally and are separate from git. Use git for permanent version control.

## What if Agent sets CI=1 in terminal commands?

Cursor sets `CI=1` as an environment variable when running terminal commands through Agent. This helps terminal tools produce cleaner output. If your project behaves differently when `CI=1` is set (for example, skipping interactive prompts or using CI-specific paths), you can unset it in your commands:

```bash
unset CI && your-command-here
```

Or add this to a rule so Agent always unsets it:

```md
When running terminal commands, prefix with `unset CI &&` if the command's behavior changes in CI environments.
```

## What if I see "Agent Execution Timed Out"?

This error means Cursor's extension host didn't finish starting within 60 seconds, so Agent features couldn't initialize. The same root cause shows up as "Timeout waiting for EverythingProvider" in network diagnostics.

Causes vary, so collect logs before changing anything:

1. Press **Cmd/Ctrl+Shift+P** and run **Developer: Export Logs...**
2. Select **Main**, **Window**, and **Extension Host**
3. Also check **Output → Extension Host** (Cmd/Ctrl+Shift+P → "Output", then pick "Extension Host" from the dropdown). If it's empty, take a screenshot; an empty panel is a strong diagnostic signal.
4. Share the exported zip and screenshot with support, along with your OS and Cursor version.

On managed or enterprise machines, endpoint security software (antivirus, EDR) is one possible cause. If your IT team confirms a security agent is active, share the [Endpoint Security Configuration](https://cursor.com/docs/enterprise/endpoint-security.md) page so they can add the right process and path exclusions.

## How do I report a bad Agent response?

1. Click the **...** menu at the bottom of the response and select **Copy Request ID**.
2. Post to [forum.cursor.com](https://forum.cursor.com/) with the request ID, steps to reproduce, and your system info (found in **Cursor > About Cursor** on macOS or **Help > About** on Windows/Linux).

## Related

- [Agent reference](https://cursor.com/docs/agent/overview.md)
- [Plan Mode](https://cursor.com/docs/agent/plan-mode.md)
- [Rules](https://cursor.com/docs/rules.md)
- [Terminal sandbox](https://cursor.com/docs/agent/tools/terminal.md)
- [Endpoint security configuration](https://cursor.com/docs/enterprise/endpoint-security.md)
- [Network and proxy](https://cursor.com/help/troubleshooting/network.md)
- [MCP troubleshooting](https://cursor.com/help/customization/mcp.md#how-do-i-troubleshoot-mcp-servers)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
