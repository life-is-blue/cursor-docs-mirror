# Performance

If Cursor is running slowly or using too many resources, try these fixes.

## How do I reduce high CPU or memory usage?

High usage typically stems from extensions or settings issues.

- Disable extensions you don't need. Run `cursor --disable-extensions` to test, then re-enable one at a time to find the cause.
- Add large generated folders to `.cursorignore` (e.g., `dist/`, `build/`, `.next/`)

## How do I speed up codebase indexing?

For large repositories, initial indexing can take time. To speed it up:

- Add generated code and build artifacts to `.cursorignore`
- Make sure `node_modules` and similar dependency folders are in `.gitignore` (Cursor respects `.gitignore` for indexing)

## How do I reduce editor input delay?

Disable extensions one at a time to identify the cause. You can also run `cursor --disable-extensions` from the command line to test without any extensions.

## Related

- [Ignore files](https://cursor.com/help/customization/ignore-files.md)
- [Installation and startup](https://cursor.com/help/troubleshooting/install-issues.md)


---

## Sitemap

[Overview of all docs pages](/llms.txt)
