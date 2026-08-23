# Cursor Router

Cursor Router is the intelligent routing behind Auto. It sends each request to a model that fits the task, with Cost, Balance, and Intelligence modes.

## What is Cursor Router and how is it different from the previous Auto mode?

Cursor Router is the relaunched Auto mode. A machine-learning classifier routes each Auto request across a pool of models instead of you picking one yourself.

Instead of choosing a specific model, you select **Auto**. The router analyzes each request and sends it to the model that delivers comparable results at lower cost for that task.

Compared with the previous Auto mode:

- Legacy Auto is now called **Cost** in the Auto selection menu
- **Balance** is the default mode for new users
- Balance and Intelligence bill at the routed model's cost, while Cost keeps the previous bundled Auto pricing

See [available models](https://cursor.com/help/models-and-usage/available-models.md#which-models-does-cursor-router-route-across) for the current routing pool.

## How does Cursor Router decide which model to use for my request?

An ML classifier runs on each agent request and routes by task type and complexity. Simple requests go to fast, cost-efficient models. Complex work goes to frontier models.

The goal is to pick the cheapest model that still produces comparable results for that request. Routing is data-driven and not configurable per request. You steer outcomes by choosing an optimization mode: Cost, Balance, or Intelligence.

If a model is blocked on your team, the router skips it and falls back to an allowlisted alternative. Blocking required models can disable the router entirely. See [available models](https://cursor.com/help/models-and-usage/available-models.md#which-models-does-cursor-router-route-across) for details.

## What are the Cost, Balance, and Intelligence optimization modes and how do I switch between them?

Open the model picker, select **Auto**, then choose an optimization mode:

- **Cost**: Equivalent to the legacy Auto mode. Keeps bundled Auto pricing unchanged. Choose this when you want spend closer to earlier Auto levels.
- **Balance**: The default mode for new users. Aims for strong results while controlling cost across the model pool.
- **Intelligence**: Routes to more capable models. Recommended for complex, multi-step work. Delivers about 20 to 30% higher quality by picking among first-party models in the pool.

Team admins can limit which modes members see and set the team default. See [manage your team](https://cursor.com/help/account-and-billing/teams-management.md#how-do-admins-enable-disable-or-configure-cursor-router-for-their-team) for admin controls.

## Can I use Cursor Router from the SDK?

Yes. In the [TypeScript SDK](https://cursor.com/docs/sdk/typescript.md#cursor-router) and [Python SDK](https://cursor.com/docs/sdk/python.md#cursor-router), Router is model id `auto-smart` with parameter `optimize_for` set to `cost`, `balanced`, or `intelligence`. Call `Cursor.models.list()` first to confirm Router is available for the API key's team.

## Related

- [Available models](https://cursor.com/help/models-and-usage/available-models.md)
- [TypeScript SDK: Cursor Router](https://cursor.com/docs/sdk/typescript.md#cursor-router)
- [Python SDK: Cursor Router](https://cursor.com/docs/sdk/python.md#cursor-router)
- [Manage your team](https://cursor.com/help/account-and-billing/teams-management.md)
- [Usage and limits](https://cursor.com/help/models-and-usage/usage-limits.md)
- [Usage-based charges](https://cursor.com/help/account-and-billing/overages.md)
- [Models & Pricing](https://cursor.com/docs/models-and-pricing.md)
- [Teams pricing](https://cursor.com/docs/account/teams/pricing.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
