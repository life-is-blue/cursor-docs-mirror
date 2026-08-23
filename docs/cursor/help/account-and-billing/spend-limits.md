# Spend limits

Set spending limits to prevent unexpected on-demand charges. When a limit is reached, AI features stop for that user until the next billing cycle.

## How do I set a spend limit?

1. Go to your [dashboard](https://cursor.com/dashboard/spending) under the **Spending** tab
2. On-demand usage must be enabled to view and set spend limits
3. Set a monthly spend limit for yourself or your team

Limit changes take effect immediately. Setting a limit to "No Limit" removes it.

## Who can change spend limits?

On Teams and Enterprise plans, whether team members can enable or disable on-demand usage and change the team-level spend limit depends on the **Only Admins Can Edit Usage Settings** toggle under **Permissions** in the [Spending tab](https://cursor.com/dashboard/spending):

- **When the toggle is off**, any team member can change these settings.
- **When the toggle is on**, only team admins can.

To restrict these controls to admins:

1. As a team admin, go to the [Spending tab](https://cursor.com/dashboard/spending)
2. Under **Permissions**, enable **Only Admins Can Edit Usage Settings**

Once enabled, team members can still view the Spending tab, but only admins can change on-demand usage and team-level limits. Member-level and group-level overrides on Enterprise plans are always admin-only.

Enterprise admins can review changes to this setting in the [audit log](https://cursor.com/docs/enterprise/compliance-and-monitoring.md#audit-logs) under the `admin_only_usage_pricing` event.

## What happens when a spend limit is reached?

- AI features stop working for that specific user
- Other team members continue unaffected
- The user sees a notification that their limit was reached
- Usage resumes automatically at the start of the next billing cycle

## What types of spend limits are available?

**Individual plans (Pro, Pro+, Ultra):** Set a monthly spend limit for your on-demand usage.

**Teams plans:** Set a team-level spend limit. When reached, all members consuming on-demand usage lose access to AI features.

**Enterprise plans:** Set both team-level and member-level limits. Member limits can be configured through:

1. Member overrides in the [Members tab](https://cursor.com/dashboard/members)
2. Group overrides in the [Groups tab](https://cursor.com/dashboard/members?subtab=active-directory)
3. Team general spend limit in the [Spending tab](https://cursor.com/dashboard/spending)

When a user has limits from multiple sources, Cursor applies the highest applicable limit. Enterprise admins can also manage limits through the [Admin API](https://cursor.com/docs/account/teams/admin-api.md#set-user-spend-limit).

## Does changing the team spend limit update existing member overrides?

No. Updating the team-level spend limit only changes the default for members who don't have a member or group override. Anyone with an existing override keeps their individual limit until you clear it.

To move a user back to the team default, remove their override in the [Members tab](https://cursor.com/dashboard/members) or [Groups tab](https://cursor.com/dashboard/members?subtab=active-directory). The same applies to limits set through the [Admin API](https://cursor.com/docs/account/teams/admin-api.md#set-user-spend-limit).

## What are dynamic spend limits?

Dynamic Spend Limits automatically adjust the team spend limit based on team size. As the number of seats grows or shrinks, the limit changes proportionally. Toggle this setting in the Spending tab.

## Do spend limits apply to pooled usage?

On Enterprise pooled usage accounts, member spend limits apply to total usage, not just on-demand.

## Related

- [Spend alerts](https://cursor.com/help/account-and-billing/spend-alerts.md)
- [Usage-based charges](https://cursor.com/help/account-and-billing/overages.md)
- [Usage and limits](https://cursor.com/help/models-and-usage/usage-limits.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
