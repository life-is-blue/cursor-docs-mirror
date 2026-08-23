# Usage and limits

Each Cursor plan includes two monthly usage pools:

- **Cursor Models**: Cursor Grok 4.6, Cursor Grok 4.5, and Composer 2.5
- **Other Models**: Third-party models, charged at model provider prices

| Plan                  | Included usage (summary)                                         |
| --------------------- | ---------------------------------------------------------------- |
| **Pro** ($20/mo)      | $20 of API agent usage + generous First-party models pool usage  |
| **Pro Plus** ($60/mo) | $70 of API agent usage + generous First-party models pool usage  |
| **Ultra** ($200/mo)   | $400 of API agent usage + generous First-party models pool usage |

See [Cursor Start](https://cursor.com/help/account-and-billing/cursor-start.md) for India plan details.

Your model selection affects how quickly your included usage is consumed.

Current usage-based plans don't include Max Mode. On legacy request-based plans, [Max Mode](https://cursor.com/help/ai-features/max-mode.md) is billed at the model's API rate plus 20%.

## How do I check my usage?

Go to the [Spending](https://cursor.com/dashboard/spending) tab in your dashboard. It shows real-time usage for both pools, remaining allowance, and any on-demand charges.

## What happens when I hit my usage limit?

You'll see a notification in the editor. You can either enable on-demand usage (pay-as-you-go) or upgrade to a higher plan.

## When does my usage reset?

Usage resets monthly with your billing cycle. Unused usage does not roll over. The reset date is shown on the [Spending](https://cursor.com/dashboard/spending) tab.

For teams, all members' usage resets at the same time based on the team billing cycle.

## How do I get more usage?

- **Use Cursor Models**: Cursor Grok 4.6, Cursor Grok 4.5, and Composer 2.5 draw from the Cursor Models pool, tracked separately and included with your plan
- **Enable on-demand usage**: Pay for additional requests at the same API rates
- **[Upgrade your plan](https://cursor.com/help/account-and-billing/pricing.md#how-do-i-upgrade-my-plan)**: Higher-tier plans include more usage

## How does Cursor Router interact with my plan's usage pools and limits?

Cursor Router requests are billed at the routed model's cost and can draw from both the Cursor Models pool and the third-party Other Models pool, depending on which model handles the request.

- **Composer 2.5** requests carry no [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md) on any plan
- **Cost** mode (legacy Auto) keeps bundled Auto pricing
- **Balance** and **Intelligence** bill at the selected model's rate under your plan

When included usage runs out, on-demand charges apply if you have on-demand usage enabled. Check your [Spending dashboard](https://cursor.com/dashboard/spending) for request-level cost and pool details.

See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for mode details.

## Related

- [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md)
- [Pricing and plans](https://cursor.com/help/account-and-billing/pricing.md)
- [Usage-based charges](https://cursor.com/help/account-and-billing/overages.md)
- [Available models](https://cursor.com/help/models-and-usage/available-models.md)
- [API keys](https://cursor.com/help/models-and-usage/api-keys.md)
- [Pricing reference](https://cursor.com/docs/models-and-pricing.md)
- [Model pricing](https://cursor.com/docs/models-and-pricing.md#model-pricing)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
