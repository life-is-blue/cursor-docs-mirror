# Extensions

Cursor uses the Open VSX extension registry for third-party extensions, with Cursor's marketplace proxy applying automated malware and supply-chain analysis before extensions are offered for install. Many popular VS Code extensions are available; some Microsoft Marketplace-only extensions are replaced by audited Anysphere builds.

## How do I install an extension?

1. Open the Extensions panel:
   - **Mac**: Press Cmd + Shift + X
   - **Windows/Linux**: Press Ctrl + Shift + X
2. Search for the extension you want
3. Click **Install**

The extension activates immediately.

## Do all VS Code extensions work?

Cursor uses [Open VSX](https://open-vsx.org) for third-party extensions.

**What that means for you:**

- Most popular extensions are available on Open VSX, but not every Microsoft Marketplace extension is listed there.
- The same `publisher.extension` name can point to different publishers or code on Open VSX than on the Microsoft Marketplace. Treat extension IDs like dependencies: install from publishers you trust.
- Cursor publishes first-party **Anysphere** replacements for some widely used extensions that are unavailable on Open VSX.

**How Cursor reduces supply-chain risk:**

Cursor routes extension search and downloads through its own marketplace proxy (`marketplace.cursorapi.com`), not a direct passthrough to Open VSX. Before an extension is shown in search or served as a download, Cursor runs automated malware and supply-chain analysis using commercial security tooling. Extensions that fail review are blocked. Cursor also monitors extension-ecosystem threat intelligence and updates its blocklist over time.

Publisher verification, enterprise allowlists, optional signature verification, and install cooldowns (below) add further layers. No single control replaces the others.

## Enterprise and team extension controls

If you manage Cursor for a team, you can add defense in depth on top of Cursor's marketplace analysis.

### Marketplace Install Cooldown

Team admins can defer extension installs and updates until a marketplace version has been published for a minimum number of hours. This gives a buffer against short-lived malicious uploads.

- **Where to configure:** [Team settings](https://cursor.com/dashboard/team-settings) → **Security & automation** → **Marketplace Install Cooldown (hours)**
- **Who can configure:** Team owners and admins
- **Default:** `0` (disabled). Set the number of hours to a value your organization accepts based on its risk posture.
- **Behavior:** When set above `0`, the value is applied fleet-wide and overrides per-user `extensions.installCooldownHours` settings so developers cannot opt back into instant updates.

Individual users can also set `extensions.installCooldownHours` in their own settings when the team has not enforced a cooldown.

### Allowed extensions

Restrict installs to approved publishers or extension IDs. Configure in the [team dashboard](https://cursor.com/dashboard/team-settings) or via MDM (`AllowedExtensions`). See [Allowed extensions](https://cursor.com/docs/enterprise/identity-and-access-management.md#allowed-extensions).

### Extension signature verification

Enterprise teams can require valid Open VSX extension signatures before install. Configure in [Team settings](https://cursor.com/dashboard/team-settings) → **Security & automation** → **Require Extension Signature Verification**.

> **Note:** Install cooldown and signature verification are client-side install controls. They complement, but do not replace, marketplace-layer analysis and blocking.

## How do I disable an extension?

Open the Extensions panel, find the extension, and click **Disable**. You can disable extensions globally or for the current workspace only.

If an extension is causing performance issues or conflicts with Cursor's AI features, try disabling it to see if the problem resolves.

## How do I get my extension verified?

Extension publishers can request a verification badge in the marketplace. Verified publishers have undergone additional security review and identity confirmation. Verification confirms publisher identity. It is one layer of trust; enterprises should still use allowlists and install cooldowns for extensions that access production code and credentials.

To request verification:

1. Add a link to your OpenVSX listing on your public website (such as in the installation section). This must be a website with its own domain name; a GitHub readme is not supported.
2. Update the "homepage" link on your OpenVSX listing to point to this website.
3. If your extension is published on multiple marketplaces, use the same extension ID on OpenVSX as you do elsewhere.
4. Create a post in the [Extension Verification category](https://forum.cursor.com/c/showcase/extension-verification/23) on the Cursor forum with your extension name and a link to your website where we can verify the OpenVSX registry link.

We'll verify the link and add the verification badge to your publisher name once approved.

## Related

- [Extension conflicts](https://cursor.com/help/troubleshooting/extensions.md)
- [Allowed extensions (enterprise)](https://cursor.com/docs/enterprise/identity-and-access-management.md#allowed-extensions)
- [Enterprise deployment and MDM](https://cursor.com/docs/enterprise/deployment-patterns.md)
- [LLM safety and controls](https://cursor.com/docs/enterprise/llm-safety-and-controls.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
