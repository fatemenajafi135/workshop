# How the attendee version is made (for you, not for attendees)

`main` holds the **full** agent in `agent/`. This folder holds what attendees get *instead* of 7 of those files, plus the guides.

```
main                                            workshop (generated)
────                                            ────────────────────
agent/                  the full code    ────►  solutions/   the 7 full files
workshop_files/
  todo_versions/        the 7 TODO files ────►  agent/       the TODO versions (+ the shared files)
  WORKSHOP.md, SETUP.md, README.md       ────►  the same names at the root
```

- **To change what attendees get:** edit the files here (or the real ones in `agent/`), commit on `main`, then run `python3 tools/build_workshop.py`.
- **Never edit the `workshop` branch by hand.** It's thrown away and rebuilt each time.
- **The 7 files that differ:** `core.py` and the 6 files in `missions/` (permission, stop_check, budget, trimming, caching, prompt). Everything else in `agent/` (llm, sandbox, trace, ...) is shared.
- **Keep them in step:** if you change a function signature in `agent/`, change its TODO version here too. The free tests (`make check-mission`) will tell you if they drift.
- This whole folder is deleted from the `workshop` branch, so attendees never see it.
