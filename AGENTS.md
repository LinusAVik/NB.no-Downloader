# AGENTS.md

- Preserve the tile-based `geneza` resolver. Do not replace it with `/full/` image requests unless current NB.no behavior has been verified.
- Never commit, print, log, or expose cookie/session values. `nb_cookie.txt` must stay ignored.
- Preserve retry and resume behavior. Existing page JPGs should be reusable after interruption.
- Treat HTTP 400/403/404 carefully: NB.no may use them for nonexistent tiles/pages, not only authentication failures.
- Test changes on 1–2 pages before any full-book run.
- Do not overwrite an existing full PDF during tests. Use a separate test output or warn explicitly first.
- Keep Python 3 compatibility on macOS and Windows.
- Preserve attribution to the upstream `akselsd/NB.no-Downloader` project.
