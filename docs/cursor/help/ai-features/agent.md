# Agent mode

Agent is Cursor's AI assistant. It searches your codebase, edits multiple files, runs terminal commands, and fixes errors on its own.

## What can Agent mode do?

Agent can build features from scratch, refactor existing code, fix bugs, write tests, and run shell commands. Give it a task in plain language and it figures out which files to read, what changes to make, and how to verify the result.

## How do I start using Agent?

1. Open the Agent panel:
   - **Mac**: Press Cmd + I
   - **Windows/Linux**: Press Ctrl + I
2. Type your request. Be specific about what you want. For example: "Add a login form to the homepage with email and password fields."
3. Press Return. Agent starts exploring your codebase and making changes.
4. Watch edits appear in the diff view as they happen.

You can also run agents from the browser at [cursor.com/agents](https://cursor.com/agents) using Cloud Agents.

## How do I interrupt Agent?

Click the **Stop** button to stop Agent mid-task. This lets you redirect or start a different approach.

## How do I review Agent changes?

Agent's edits are applied as it works. Review them in the diff view and reject anything you don't want. For PR-level reviews, [Bugbot](https://cursor.com/help/ai-features/bugbot.md) can catch bugs and security issues automatically.

## How do I undo Agent changes?

Hover over a previous message and click **Restore Checkpoint** in the bottom right to roll back all changes Agent made after that point.

## Can Agent delegate tasks to subagents?

Yes. Agent can spin up specialized [subagents](https://cursor.com/docs/subagents.md) to handle research, shell commands, or browser interactions in parallel. Each subagent runs in its own context window and returns a result to the main conversation. You can also create custom subagents by adding markdown files to `.cursor/agents/`.

## Can Agent generate images?

Yes. Agent can create images from text descriptions or reference images. This is useful for UI mockups, product assets, or architecture diagrams. Generated images are saved to your project and shown inline in chat.

## Can I queue follow-up messages while Agent is working?

Yes. Submit your next instruction while Agent is busy. Your message waits in a queue and runs automatically when the current task finishes. You can drag to reorder queued messages.

## Can Agent search my past conversations for context?

Yes. Conversation search is available as an agent tool. When Agent needs context from something you discussed before, it can query your past conversations on its own. You don't need to remember which chat it was in.

## Which mode should I use?

| Mode      | Best for                                                     | Can edit files?                  |
| --------- | ------------------------------------------------------------ | -------------------------------- |
| **Agent** | Building features, refactoring, fixing bugs                  | Yes                              |
| **Ask**   | Understanding code, exploring architecture                   | No (read-only)                   |
| **Plan**  | Complex features where you want to review the approach first | Yes (after you approve the plan) |
| **Debug** | Tricky bugs that need runtime evidence                       | Yes                              |

Use Agent for most tasks. Switch to Ask when you want answers without changes. Use Plan for multi-file features where you want to review the approach. Use Debug for bugs that are hard to reproduce or understand.

## How do I switch between modes?

- Press Shift + Tab to cycle through modes
- Click the mode picker dropdown in the Agent panel

Each mode uses its own context, so switching modes starts a fresh context window. Start a new chat when changing tasks for the best results.

## Do rules apply in all modes?

Yes. Project rules, user rules, and team rules apply in Agent, Ask, Plan, and Debug modes. The rules are included in every conversation regardless of which mode you're using.

## Related

- [Ask mode](https://cursor.com/help/ai-features/ask-mode.md)
- [Plan mode](https://cursor.com/help/ai-features/plan-mode.md)
- [Debug mode](https://cursor.com/help/ai-features/debug-mode.md)
- [Side chats](https://cursor.com/help/ai-features/side-chats.md)
- [Conversation search](https://cursor.com/help/ai-features/conversation-search.md)
- [What are coding agents?](https://cursor.com/help/ai-features/coding-agents.md)
- [What is agentic coding?](https://cursor.com/help/ai-features/agentic-coding.md)
- [What is multi-agent coding?](https://cursor.com/help/ai-features/multi-agent.md)
- [Subagents reference](https://cursor.com/docs/subagents.md)
- [Modes reference](https://cursor.com/docs/agent/plan-mode.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
