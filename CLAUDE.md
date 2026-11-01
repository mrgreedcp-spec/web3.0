@AGENTS.md

## Claude Code specifics

- `AGENTS.md` above is the single source of truth for project rules; edit it there, not here.
- If a hook blocks an edit or a commit, fix the content it points out.
  Do not work around the hook (for example by writing the file through Bash instead of Edit).
- Some environments inject a `Co-Authored-By:` trailer into the default commit instructions.
  The project rule wins: leave that trailer out.
