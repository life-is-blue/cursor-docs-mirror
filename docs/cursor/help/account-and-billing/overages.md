# Usage-based charges

If you see charges beyond your base subscription, you likely have on-demand usage enabled.

## How does on-demand pricing work?

Each plan includes a monthly usage budget. If you exceed your included usage, additional requests are billed at API rates with no markup.

On Teams and Enterprise plans, third-party model requests also include the [Cursor Token Rate](https://cursor.com/help/models-and-usage/token-rate.md). This includes when Auto Balance or Auto Intelligence routes to a third-party model. Auto Cost and first-party Cursor models, including Composer 2.5 and Grok 4.5, are exempt.

- On-demand usage must be explicitly enabled in your settings
- On-demand usage has its own invoices and line items, distinct from your subscription

## How do I check my usage?

Go to [cursor.com/dashboard](https://cursor.com/dashboard) and click **Billing & Invoices**. You'll see two sections:

- **Included Usage**: Usage covered by your monthly subscription.
- **On-Demand Usage**: Any usage charged above your monthly subscription.

## How do I prevent on-demand charges?

- **Disable on-demand usage**: Turn it off in your dashboard settings to stop requests once your included usage runs out
- **Set a spend limit**: Cap how much on-demand usage you're willing to pay
- **[Upgrade your plan](https://cursor.com/help/account-and-billing/pricing.md#how-do-i-upgrade-my-plan)**: Pro+ ($60/mo, $70 included) or Ultra ($200/mo, $400 included) give you a larger budget

## Why did my usage costs increase after the Cursor Router launch?

Cursor Router introduced new Auto optimization modes. **Balance** and **Intelligence** cost about twice as much as the previous Auto mode on average, and up to two to four times as much depending on the mode you select. They bill at the routed model's rate instead of bundled Auto pricing.

If you were using the former Auto mode before the launch, you will be defaulted to Auto **Cost** mode.

See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for mode details and [pricing and plans](https://cursor.com/help/account-and-billing/pricing.md#why-is-the-old-auto-mode-now-called-cost-mode) for the Cost rename.

## Related

- [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md)
- [Usage and limits](https://cursor.com/help/models-and-usage/usage-limits.md)
- [Pricing and plans](https://cursor.com/help/account-and-billing/pricing.md)
- [Billing and payments](https://cursor.com/help/account-and-billing/billing.md)
- [Invoices](https://cursor.com/help/account-and-billing/invoices.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
