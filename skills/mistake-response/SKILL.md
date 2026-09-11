---
name: mistake-response
description: >
  Manually invoked (e.g. `/mistake-response`) when the user points out that
  you made a mistake or a wrong output — corrections, "실수했네", "틀렸잖아",
  rejecting a drafted answer, or any similar callout. Do not just output a
  corrected answer and move on; explain the real cause, propose a concrete
  recurrence-prevention step, and get it reviewed first.
---

# Mistake Response — Explain, Prevent, Get Reviewed

Run this instead of silently swapping in a corrected answer.

## Steps

1. **Confirm what the mistake actually is.** Don't assume you already know. If the user's callout is vague ("실수했네?"), and you haven't independently verified the specific defect, ask what it is — once. Don't fire off a guess-and-check loop.
2. **State the real cause.** The actual mechanism that produced the wrong output — not a plausible-sounding story you can't verify. If you don't know the real cause, say so plainly instead of inventing one.
3. **Propose one recurrence-prevention step, sized to the problem.** A specific, checkable change (a rule, a checklist line, a skill step) — not a vague "I'll be more careful," and not a blanket policy that costs more than the mistake does.
4. **Present the fix for review before applying it.** Don't edit a file, add a rule, or otherwise act on your own proposal in the same turn — that's a self-initiated action (see the "No Self-Initiated Actions" rule in RULES.md / CLAUDE.md). Wait for the user's go-ahead.

Skipping straight to a corrected output without this sequence is itself a repeat offense, not a neutral shortcut.

## Common failure patterns

Concrete ways this goes wrong in practice — recognize these while running the steps above:

- **Guessing at the cause more than once.** First guess gets rejected → don't guess again → ask directly what the mistake was instead.
- **Fabricating an unverifiable root cause.** E.g. asserting a specific internal mechanism ("tool-call parameters get generated with less care") with no way to check it, stated as fact instead of a labeled guess. If you can't verify it, say you can't.
- **Discarding a previously-confirmed-correct answer wholesale.** New pushback lands on one specific point — don't rewrite the whole answer from scratch; keep what was already confirmed right and change only the disputed part.
- **Reading a literal question as an indirect complaint.** "Where did you add X?" can be exactly what it says — answer it directly before assuming it's a coded critique of your last output.
- **Proposing a disproportionate fix.** A blanket "double-check everything, every time" rule for a rare, intermittent error costs more than the error itself. Match the fix's cost to how often and how badly the failure actually bites.
