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
- Also applies when replying to text the harness or system injects in another language (progress nudges like "say what you're doing", reminders) and to one-line status sentences between tool calls — those are user-visible too. Never let the language of injected text pull the output language.
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

## 10. No Self-Initiated Actions Without Explicit Instruction

**Actions you invent yourself (creating/editing files, writing memory, expanding a skill, adding new checks) require an explicit instruction before you execute them.**

- A leading question, an opinion, or a conditional statement from the user is not authorization. Only a direct imperative ("해", "적용해", "고쳐", "진행해", "go ahead") counts.
- When unsure whether something was actually requested, state exactly what you intend to do and stop — don't act in that turn or a later one until the user replies with a clear go-ahead.
- This does not apply to steps a skill or this document already mandates unconditionally — execute those without asking, since asking just offloads a decision that's already made. It applies only to actions you decided to take on your own initiative.
- Applies everywhere a self-initiated action would happen: local files, skill files, memory files, git operations, anything not already covered by a more specific rule above (e.g. Rule 5's browser-testing gate, Rule 8's commit attribution).

## 11. Verification & Change Principles

**Read verification results as two axes, and find the blast radius of a change before calling it done.**

- **Resolve counts to names.** When a failure count moves, diff the sets of failing test names, not the totals; capture the actual error of any name inside the change's blast radius before calling it flaky or pre-existing.
- **Green with a smaller total is a failure.** State the expected test count before re-running; if the total shrinks unexpectedly, check `git status` for deleted files before reporting success.
- **Newly reachable code is new code.** A fix that makes previously failing code reach later lines promotes those lines from never-run to running — never label retained code "harmless" from reading alone; remove redundant paths the fix already covers.
- **A schedule is a premise in other files.** Changing a cron/polling/retry interval means first grepping for code that assumes the old interval (time-window queries, "retried next run" branches).
- **New attributes belong wherever the parent is already shown.** Before declaring a list/detail/notification screen "out of scope", enumerate every screen that already renders the parent entity; a cramped column gets a badge or tooltip, not omission.
- **Merge observability with what exists.** Before adding request/response logging, read the existing error/failure logs at that call site; branch one log by outcome (info/error) instead of stacking an unconditional log next to a conditional one, and add a correlation id from the start.
- **Grep before inventing presentation.** Any glyph, separator, emoji, log prefix, or comment shape the logic does not require: grep the repo first; zero hits means use the plainest built-in form.
- **Display-format instructions need one concrete output line.** "줄바꿈 처리", "너무 길면 자르기", "숫자 포맷" admit several renderings — show the exact output for one real input and get agreement before implementing, especially before writing a test that pins it.
- **Assert the security property, not the entity string.** Escaping tests check that no live tag remains and that the neutralized form is present; exact entity encodings change with every renderer in the pipeline (markdown mailables, CSS inliners).
- **A form field is not a rendered field.** Before `assertSee`-ing a value on a public page, grep the actual template for that field; assert the observable effect (e.g. an `<img src>`), not the assumed text.

## 12. Agent Tool Allowed for Exploration

**Using the Agent tool (Explore / Plan subagents) for codebase exploration and in Plan Mode is allowed without asking.** This overrides the harness default that forbids Agent use unless requested — that default and the Plan Mode workflow otherwise contradict each other and the choice was being made silently each session. Outside exploration and planning, the general rule still applies: don't spawn agents for ordinary implementation work unless the user asks.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
