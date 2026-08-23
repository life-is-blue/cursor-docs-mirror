# Available models

Cursor supports a range of AI models from multiple providers.

## How do I switch models?

Open the model selector in your chat or agent panel and choose the model you want, or press Cmd + / to cycle through models. Your selection persists across conversations until you change it.

## Which models are available?

Cursor offers its own models ([Grok 4.5](https://cursor.com/help/models-and-usage/grok-4-5.md) and [Composer](https://cursor.com/docs/models/cursor-composer-2-5.md)) in the Cursor Models pool alongside other frontier models from OpenAI, Anthropic, and Google. The available models depend on your plan. Hobby users have access to a smaller set, while paid plans unlock all models.

See the [models reference](https://cursor.com/docs/models-and-pricing.md) for the complete list, context window sizes, and capabilities.

## Which model should I use?

- **Auto** selects models that balance intelligence, cost, and reliability. Good for everyday tasks. See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for Cost, Balance, and Intelligence modes.
- **[Grok 4.5](https://cursor.com/help/models-and-usage/grok-4-5.md)** is Cursor's flagship model. The smartest model Cursor has trained, built for the hardest tasks.
- **Composer** is Cursor's fast, cost-efficient model. Capable for most tasks, and built for interactive coding.
- **Claude Opus** and **GPT-5.6 Sol** handle complex, multi-step tasks well.
- Some users also prefer **Gemini Pro** models.

See the [models reference](https://cursor.com/docs/models-and-pricing.md) for the full list.

## Which models does Cursor Router route across?

Cursor Router routes across these models:

- **[GPT-5.5](https://cursor.com/docs/models/gpt-5-5.md)**
- **[Claude Opus 5](https://cursor.com/docs/models/claude-opus-5.md)**
- **[Grok 4.5](https://cursor.com/help/models-and-usage/grok-4-5.md)**
- **[Claude Fable 5](https://cursor.com/docs/models/claude-fable-5.md)**

**Required:** [Grok 4.5](https://cursor.com/help/models-and-usage/grok-4-5.md). The router needs a powerful, cost-efficient model in the pool; blocking Grok 4.5 disables the router.

**Recommended:** GPT-5.5 and Claude Opus 5. Blocking one reduces routing quality. Blocking both disables the router.

Blocked models (enterprise plans) are skipped and the router falls back to an allowlisted alternative when possible.

Team admins manage model access from [Team Settings > Models](https://cursor.com/dashboard/team-settings/models). See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for routing details.

To use Router from code, call `Cursor.models.list()` in the [TypeScript SDK](https://cursor.com/docs/sdk/typescript.md#cursor-router) or [Python SDK](https://cursor.com/docs/sdk/python.md#cursor-router) and look for model id `auto-smart` with parameter `optimize_for`.

## Can I see which model Cursor Router used for my request?

By default, the routed model identity is hidden so you judge results on merit. Team admins can change this to **Displayed** in the admin dashboard so members see which model handled each request.

If model visibility is set to Displayed, check the model picker or request details in your chat after each turn. See [manage your team](https://cursor.com/help/account-and-billing/teams-management.md#how-do-admins-enable-disable-or-configure-cursor-router-for-their-team) for admin controls.

## How much does Auto cost?

Auto has three modes with different pricing:

- Auto Cost pricing is set per million tokens, regardless of which model is used: $1.25 per 1M input + cache write, $6.00 per 1M output, and $0.25 per 1M cache read.
- Auto Balance and Auto Intelligence are charged at Model API rates for the model used, based on actual usage. Third-party models also incur the [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md).

See [Auto modes](https://cursor.com/docs/models-and-pricing.md#auto-modes) on Models & Pricing for details.

**Balance** and **Intelligence** bill at the routed model's rate instead. See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for mode details.

## How much does Grok 4.5 cost?

Grok 4.5 has two speeds, each with its own token rates:

- **Standard**: $2.00 per 1M input tokens, $6.00 per 1M output tokens, $0.50 per 1M cache read tokens
- **Fast**: $4.00 per 1M input tokens, $18.00 per 1M output tokens, $1.00 per 1M cache read tokens

Grok 4.5 draws from the Cursor Models usage pool included with your plan. See the [models reference](https://cursor.com/docs/models-and-pricing.md) for current rates.

## How much do models cost?

Each model has its own per-token rate set by the provider (OpenAI, Anthropic, Google, etc.). Cursor charges at these published API rates with no markup. Your model choice directly affects how quickly your included usage budget is consumed.

For the full pricing table, see [model pricing](https://cursor.com/docs/models-and-pricing.md#model-pricing).

## What model am I talking to?

The active model is shown in the model picker at the top of the chat panel. If you selected **Auto**, Cursor Router picks the model for each request and the specific model can vary between turns.

When your team admin sets model visibility to **Displayed**, you can see which routed model handled each request. Otherwise the routed model stays hidden. See [manage your team](https://cursor.com/help/account-and-billing/teams-management.md#how-do-admins-enable-disable-or-configure-cursor-router-for-their-team) for admin controls.

You can click the model picker at any time to see or change your selection.

## What models do subagents use?

Built-in subagents (Explore, Bash, Browser) select their model automatically based on the subtask. Custom subagents default to `inherit`, which uses the parent agent's model. You can override this by setting the `model` field in the subagent's YAML frontmatter to a specific model ID.

See [subagent model configuration](https://cursor.com/docs/subagents.md#model-configuration) for details.

## What does "model not available" mean?

Some models may not be available in certain regions based on restrictions set by the model providers (not Cursor). When this happens, those models won't appear in Cursor.

Workarounds:

- **Use Auto**: Auto is available in all regions and selects an available model for each request
- **Try other providers**: Some providers may have fewer regional restrictions. Check each provider's supported-regions page for details.
- **Bring Your Own API Key**: If you have an API key from a provider that serves your region, add it in **Cursor Settings** > **Models**. Calls may still fail if the provider blocks your region even with your own key.

See the [regions reference](https://cursor.com/docs/account/regions.md) for provider-specific availability details.

## Related

- [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md)
- [Grok 4.6](https://cursor.com/help/models-and-usage/grok-4-6.md)
- [Grok 4.5](https://cursor.com/help/models-and-usage/grok-4-5.md)
- [API keys](https://cursor.com/help/models-and-usage/api-keys.md)
- [Usage and limits](https://cursor.com/help/models-and-usage/usage-limits.md)
- [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md)
- [Models reference](https://cursor.com/docs/models-and-pricing.md)
- [Model pricing](https://cursor.com/docs/models-and-pricing.md#model-pricing)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
