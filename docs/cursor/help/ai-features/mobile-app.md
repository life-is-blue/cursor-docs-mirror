# Cursor for iOS

Cursor for iOS is the Cursor mobile app for controlling agents running [in the cloud](https://cursor.com/help/ai-features/cloud-agents.md) and on your own computer. You start agents, watch them work in real time, and review and merge their pull requests from your iPhone or iPad. See the [Cursor for iOS reference](https://cursor.com/docs/cloud-agent/mobile.md) for a full feature tour.

The app is in beta, so features can change before general availability.

## Is there an Android app?

Not yet. The native app runs on iPhone and iPad. An Android version is planned, but there's no release date.

## Which devices and versions are supported?

iPhones running iOS 26.0 or later and iPads running iPadOS 26.0 or later.

## What is different on iPad?

The iPad layout keeps chats in a sidebar, lets you open a review next to a chat, and gives file diffs more space. You can also attach a screenshot and draw on it with Apple Pencil.

## Which countries and languages does the app support?

The app is available in all App Store regions except mainland China. The interface is English only for now, with no other languages yet.

## Who can use the app?

The app directs agents running [in the cloud](https://cursor.com/help/ai-features/cloud-agents.md) and on your own computer (using Remote Control), both of which need a paid plan to start a run. There's no separate invite or mobile entitlement beyond that: anyone who can sign in and reach [cursor.com/agents](https://cursor.com/agents) can use the app. Free accounts can sign in, but won't be able to start agents. If your organization requires SSO, you sign in through it first.

## Why don't I see any repositories?

The repository picker pulls from the source control you've connected on the web. If nothing is connected, the list is empty. The app can't set up integrations; it only uses what's already connected.

To fix it:

1. Go to [cursor.com](https://cursor.com) and connect [GitHub or GitLab](https://cursor.com/help/integrations/github-gitlab.md) in your settings.
2. Back in the app, pull down on the inbox to refresh. Your repositories appear once the connection syncs.

If the picker is also empty on cursor.com/agents, the integration isn't connected yet. If repos show on the web but not in the app, sign out and back in to re-sync.

## Can I edit code or use a terminal in the app?

No. The app is built for directing and reviewing agents, not for editing. There's no editor, terminal, or file browser. You see an agent's changed files in the diff view, then review and merge from there. For full editing, use the desktop app or [cursor.com/agents](https://cursor.com/agents).

## Where do agents I start on mobile show up?

Everywhere. Agents you start in the app appear at [cursor.com/agents](https://cursor.com/agents), in the desktop Agents window, and in the app itself. Start an agent on your phone and pick it up on your laptop later. Each surface lets you filter for the agents you started on mobile.

## Can I direct agents running on my own computer?

Yes. Besides cloud agents, you can run agents on your own computer and steer them from your phone:

- **Remote Control.** Hand off an agent you're running on your computer, then keep directing it from your phone. Remote Control requires Cursor client version 3.9.8 or later on your computer. It's only available in the [Agents Window](https://cursor.com/docs/agent/agents-window.md). Turn on Remote Control in **Settings > Agents**, run `/remote-control` in the agent's input, and open the session in the app. The agent loop moves to the cloud while its tools keep running on your machine. Remote Control is in beta and needs a paid plan.

Keep your computer awake, connected, and with the workspace open while a session runs. On Teams and Enterprise plans, an admin enables Remote Control before you can use it. See the [Cursor for iOS reference](https://cursor.com/docs/cloud-agent/mobile.md#remote-control) for the full setup.

## Why do my agents feel slow on mobile?

Cloud Agents take time to start. Each run sets up an environment, installs dependencies, and runs updates before it does the work. This is normal, and it's the same whether you start the agent on mobile or the web. If the same agent is just as slow on cursor.com/agents, it's cloud-agent setup time, not a mobile issue.

If an agent is clearly further along on the web than in the app, check your connection. The chat stream reconnects after network changes and pauses while the app is in the background, then catches up when you return. Pull down on the inbox to refresh.

## How do Live Activities work?

Live Activities show your running agents on the lock screen and Dynamic Island, tracking up to eight at once with their current state. They need the system permission enabled in iOS Settings under Cursor.

## The app is stuck or out of date. What should I do?

Try these in order:

1. **Update the app.** Open the App Store, tap your profile icon, and update Cursor.
2. **Refresh.** Pull down on the inbox to re-sync from the backend.
3. **Reinstall as a last resort.** Deleting and reinstalling clears stale local data and re-syncs on next launch. You rarely need this.

## How do I report a problem with the app?

Include these details so we can help fast:

- Your device and iOS version, from **Settings > General > About**.
- Your app version, from the app's settings (tap your profile in the upper left and scroll to the version footer).
- If a Cloud Agent is involved, its background composer ID, which you can find for that agent at [cursor.com/agents](https://cursor.com/agents).
- A screenshot or screen recording of the problem, if you can capture one.

## Related

- [Cloud Agents](https://cursor.com/help/ai-features/cloud-agents.md)
- [What are background agents?](https://cursor.com/help/ai-features/background-agents.md)
- [Automations](https://cursor.com/help/ai-features/automations.md)
- [Cursor for iOS reference](https://cursor.com/docs/cloud-agent/mobile.md)
- [Cloud Agent reference](https://cursor.com/docs/cloud-agent.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
