# Manage your team

Add and remove team members, manage seats, and track usage.

## How do I add a new team member?

1. Go to [cursor.com/dashboard](https://cursor.com/dashboard)
2. Click **Invite Members**
3. Enter the email addresses of the people you want to add

New seats are prorated based on the number of days remaining in the billing cycle. When someone joins a team, any existing individual Pro subscription on their account is automatically canceled.

Teams and Enterprise plans also support [SSO](https://cursor.com/docs/account/teams/sso.md) and [SCIM](https://cursor.com/docs/account/teams/scim.md) for automated member provisioning.

## How do I remove a team member?

1. Go to your team dashboard
2. Find the member you want to remove
3. Click **Remove** next to their name

If the member has any usage during the current cycle, their seat remains billable until the billing period ends.

Team members cannot leave a team on their own. They need to ask an admin to remove them.

## What if my team admin has left?

Check if there are other admins on the team who can help. If not, [contact support](https://cursor.com/help.md) for help recovering admin access.

## How do I view team usage?

Sign in as an admin and go to [cursor.com/dashboard](https://cursor.com/dashboard) to see individual member usage, total usage, and trends over time.

## How do admins enable, disable, or configure Cursor Router for their team?

From the team admin dashboard:

1. Go to [cursor.com/dashboard](https://cursor.com/dashboard) and open your team settings
2. Enable or disable Cursor Router for the team or for specific groups. When settings overlap across groups, Cursor uses most-permissive-wins reconciliation
3. Choose which optimization modes members can select, and set the default mode (e.g. expose only Intelligence, or turn off Legacy)
4. Set routing model visibility to **Hidden** (default) or **Displayed**. Hidden keeps the routed model identity private so results are judged on merit. Displayed shows members which model handled each request

Enterprise teams start with Cursor Router off. An admin must opt in before members can use it.

See [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md) for how routing and optimization modes work.

## Can I require team members to use Cursor Router instead of manually picking a model?

Yes. Admins can standardize on Auto with two enforcement levels. Both are off by default:

- **Soft**: Each new chat defaults to Auto. Members can still switch to another model.
- **Hard**: The model picker is locked to Auto. Members cannot override the selection.

Configure enforcement from the team admin dashboard alongside other Cursor Router settings.

## Related

- [Set up a team](https://cursor.com/help/account-and-billing/teams-setup.md)
- [Cursor Router](https://cursor.com/help/models-and-usage/cursor-router.md)
- [Team members, roles, and seat types reference](https://cursor.com/docs/account/teams/members.md)
- [Team dashboard reference](https://cursor.com/docs/account/teams/dashboard.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
