# Side chats

Side chats are durable child conversations attached to a parent agent. They use the parent thread as reference context while keeping their own visible transcript.

## What is a side chat and how does it differ from the main agent conversation?

A side chat is a full agent conversation that runs next to your main chat. The parent's conversation history is copied in as reference context for the model. That history does not appear in the side-chat transcript.

By default, side chats focus on reading, searching, and answering, so the main agent keeps working uninterrupted. A regular conversation stands on its own. A side chat stays attached to its parent and workspace, so you can explore a side question or dig into a selection without crowding the main thread.

## How do I open a side chat?

You can open a side chat in these ways:

1. Type `/side` in the chat input to open an empty side chat. You can also append your question after the command to open the side chat and send the prompt right away.
2. Select text or a diff in the chat, then choose **Ask in Side Chat** from the selection menu
3. Use a shortcut to populate a side chat with the current transcript selection:

- **Mac:** Shift+Cmd+S
- **Windows/Linux:** Shift+Ctrl+S

The new side chat starts with context from the main conversation.

## How do I bring side chat context back into the main conversation?

@-mention the side chat in the main thread. Cursor pulls that side chat's context into the main conversation so you can keep building on what you found.

## Does the parent conversation appear inside the side chat?

The parent history is available to the model as hidden reference context. It is not rendered in the side-chat transcript. Only your side-chat prompt and any follow-ups show up in the side chat.

## Can I send follow-up messages in a side chat after the first reply?

Yes. A side chat is a full durable conversation. Follow-up messages stay in the side chat and do not appear in the parent transcript.

## How do I close or archive a side chat?

Click the **X** (close) button on a side chat to archive it. Closing archives the side-chat agent; it does not delete the conversation. The durable thread stays usable until you archive it by closing it.

## Is a side chat the same thing as forking a conversation?

No. Forking creates a full copy of the parent conversation, including all messages and subagents. A side chat only seeds the model with the parent history as hidden context. It does not reproduce the parent transcript. A side chat is a parallel thread, not a fork.

## Can I create a side chat inside another side chat?

No. Nesting is not supported. A side chat cannot spawn its own side chats. Start new side chats from the parent conversation instead.

## Do side chats work with Cloud Agents?

Side chats are local-only for now. They are not currently available for Cloud Agents, but support for this is coming soon. For cloud workflows, see [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md).

## What happens to a side chat if I start a new parent conversation?

A side chat is scoped to its parent agent. If you navigate away or start a new conversation, the side chat stays attached to the original parent. It persists until you archive it.

## Related

- [Agent mode](https://cursor.com/help/ai-features/agent.md)
- [Conversation search](https://cursor.com/help/ai-features/conversation-search.md)
- [What is multi-agent coding?](https://cursor.com/help/ai-features/multi-agent.md)
- [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md)
- [Subagents reference](https://cursor.com/docs/subagents.md)
- [Agents Window](https://cursor.com/docs/agent/agents-window.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
