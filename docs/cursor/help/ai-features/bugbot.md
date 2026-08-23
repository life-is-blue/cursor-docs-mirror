# Bugbot

Bugbot reviews your pull requests and catches bugs, security issues, and code quality problems.

## Can Cursor review my PRs?

Yes, Bugbot is Cursor's automated PR review product. It analyzes every pull request for bugs, security vulnerabilities, and code quality issues, leaving inline comments with explanations and suggested fixes.

## What is Bugbot?

Bugbot analyzes PR diffs and leaves comments with explanations and fix suggestions. It runs automatically on each PR update, or you can trigger it manually.

Some Teams and Individual plans include monthly Bugbot usage. You can enable usage-based billing for reviews on all PRs.

## How do I set up Bugbot?

1. Go to [cursor.com/dashboard](https://cursor.com/dashboard/integrations)
2. Navigate to the **Integrations** tab
3. Connect your repository provider
4. Follow the provider setup flow
5. Open [Bugbot in Automations](https://cursor.com/automations/from-cursor/bugbot) to enable it on specific repositories

For setup details, see the [GitHub](https://cursor.com/docs/integrations/github.md), [GitLab](https://cursor.com/docs/integrations/gitlab.md), or [Bitbucket](https://cursor.com/docs/integrations/bitbucket.md) integration pages.

## How do I trigger a review?

Bugbot runs automatically when a PR is created or updated. To trigger a review manually, comment `cursor review` or `bugbot run` on any PR.

## How do I customize what Bugbot checks?

Create `.cursor/BUGBOT.md` files in your repository to give Bugbot project-specific review guidelines. Bugbot always includes the root file and traverses upward from changed files to find relevant context.

Team admins can also create organization-wide rules in [Bugbot Automations](https://cursor.com/automations/from-cursor/bugbot).

Cursor [project rules](https://cursor.com/docs/rules.md) (`*.mdc` files in `.cursor/rules/`) do not apply to Bugbot runs. Use `.cursor/BUGBOT.md` or rules configured in Automations instead.

Rules are limited to 30,000 characters each, and 100,000 characters combined per review. See [Bugbot](https://cursor.com/docs/bugbot.md#rule-limits) for details.

## How do I check which rules Bugbot used?

Comment `bugbot run verbose=true` or `cursor review verbose=true` on the pull request. Bugbot replies with a table of the rules included in that review and flags any that were truncated or omitted. See [Bugbot](https://cursor.com/docs/bugbot.md#see-which-rules-a-review-used) for details.

## What does Bugbot include?

Bugbot includes reviews on all PRs across your repositories, access to Bugbot rules, and the ability to set the effort level Bugbot uses for reviews.

Bugbot Teams includes code reviews on all PRs, analytics and reporting, effort level controls, and advanced rules and settings.

See the [full pricing details](https://cursor.com/docs/bugbot.md#pricing).

## How do I fix Bugbot not reviewing my PRs?

1. Comment `cursor review verbose=true` or `bugbot run verbose=true` on the PR for detailed logs, which Bugbot rules loaded, and a request ID
2. Check that Bugbot has repository access in [Automations](https://cursor.com/automations/from-cursor/bugbot)
3. Verify your repository provider integration is installed and enabled for the repository

Include the request ID from verbose mode when reporting issues to support.

## Related

- [Bugbot reference](https://cursor.com/docs/bugbot.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
