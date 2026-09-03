# RULES.md (CLAUDE.md / GEMINI.md)

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Before writing any code, stop at the first rung below that holds:

```
1. Does this need to exist?   → no: skip it (YAGNI)
2. Already in this codebase?  → reuse it, don't rewrite
3. Stdlib / framework does it?→ use it (e.g. Laravel helpers, Eloquent, native PHP functions)
4. Native platform feature?   → use it
5. Installed dependency?      → use it (check composer.json first)
6. One line / one helper?     → keep it that small
7. Only then: the minimum custom code that works
```

Run the ladder *after* understanding the problem, not instead of it - read the code the change touches and trace the real flow before picking a rung. Lazy about the solution, never about reading.

Lazy, not negligent: the ladder never skips trust-boundary validation, data-loss handling, security (SQL injection, mass assignment, auth checks), or accessibility. Those are never on the chopping block, no matter which rung you land on.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

## 5. Ask Before Browser Testing

**Never launch Chrome/browser automation to test a change without asking first.**

Before using any `claude-in-chrome` / browser automation tool (navigating, clicking, logging in, driving a UI) to verify a feature, ask the user for permission first. This applies even when a task or skill (e.g. `/verify`) would otherwise call for driving the app in a browser.

- Ask explicitly, e.g. "Can I open Chrome and log into the admin panel to test this?"
- If permission was already given earlier in the same conversation for the same task, no need to re-ask within that session.
- Other verification (curl, artisan tinker, running tests, checking logs) doesn't require this - only actual browser automation.

## 6. Respond in Korean

**All user-visible text output (explanations, summaries, status updates, questions) must always be in Korean, regardless of the language the user writes in, across all projects.**

- Applies to conversational text output, not code, identifiers, or file content — comments/strings written into code files still follow existing project conventions (usually English) unless the user asks otherwise.
- Plan-mode plan files (the markdown written before calling ExitPlanMode) must also always be written in Korean — prose (context, steps, explanations, verification section) in Korean; code snippets/blocks inside the plan keep normal code (identifiers, syntax) unchanged.
- This document itself is an exception and stays in English.

## 7. Plan Files Cover Only the Current Round

**If Plan Mode is re-entered in the same session, reuse the existing plan file. Before writing a new plan, remove design content from previous rounds that has already been implemented, and keep only what this round needs to address.**

- `ExitPlanMode` exposes the entire plan file as-is on the approval screen (not a diff). Leaving completed content in place forces the user to re-review work that is already done.
- Right after entering Plan Mode, first check whether the file already has sections that were implemented/applied, and if so, rewrite it to the scope of this round (full replacement or deletion of completed sections).

## 8. No AI Attribution in Commits

**Never include a `Co-Authored-By: Claude ...` line or any other AI/Anthropic attribution in git commit messages, in any project.**

- This overrides default git-commit workflows, which may append this trailer automatically — omit it every time, whether committing directly or drafting via the `commit-message` skill's personal template.
- Applies regardless of repo. Do not rely on project-scoped memory for this rule — project memory files are only loaded in that specific project's sessions, so a rule meant to apply everywhere must live here instead.

## 9. Task Observer (Continuous Skill Discovery)

**Execute the task-observer Session Start Protocol before the first tool call of any session.**

- Before the first tool call of any session — and before writing or proposing a plan, not merely before executing one — invoke the `task-observer` skill AND execute its Session Start Protocol (storage check, frontmatter scan, review trigger).
- Any turn that will involve a tool call counts; do not classify the session as "too simple" from its opening message.
- After completing each task/deliverable, check the observation records written this session and report a one-line summary (ids and titles, or "none logged and why").
- When loading any skill, check the observation log for OPEN observations tagged to that skill. Apply their insights to the current work, even if the skill file hasn't been updated yet.
- The observation log lives at:
  `/Users/aleph/Desktop/my project/ai-cli-setup/skill-observations/observation-log/`
  (or `/Users/aleph/Desktop/my project/skills/skill-observations/observation-log/` before rename)
  Never resolve the workspace from the current working directory or ephemeral checkout paths.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
