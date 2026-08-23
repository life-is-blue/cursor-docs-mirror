# Migrate from JetBrains

Moving from IntelliJ, WebStorm, PyCharm, or another JetBrains IDE to Cursor.

## How do I get JetBrains keybindings?

Install the JetBrains keymap extension to keep your muscle memory:

1. Open the Extensions panel (Cmd + Shift + X on Mac, Ctrl + Shift + X on Windows/Linux)
2. Search for "IntelliJ IDEA Keybindings"
3. Install the extension
4. Reload Cursor

Your familiar shortcuts now work in Cursor.

## What differences should I expect?

Cursor uses a file-and-folder project model instead of JetBrains' project system. Open a folder with **File** > **Open Folder** instead of creating a project.

Language support comes from extensions rather than built-in plugins. For most languages, install the relevant extension from the marketplace (e.g., "Python" for Python, "Go" for Go).

## Can I use Cursor without switching editors?

Yes. Cursor supports [ACP (Agent Client Protocol)](https://cursor.com/docs/integrations/jetbrains.md), which lets you connect Cursor's agent to JetBrains IDEs. You keep your IntelliJ or WebStorm setup and access Cursor's agent through the protocol.

## Related

- [Extensions](https://cursor.com/help/customization/extensions.md)
- [JetBrains integration](https://cursor.com/docs/integrations/jetbrains.md)
- [ACP documentation](https://cursor.com/docs/cli/acp.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
