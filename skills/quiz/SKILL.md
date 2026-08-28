---
name: quiz
description: Generate a 4-choice multiple-choice quiz (3-10 questions, scaled to change size) about the current uncommitted work so the user can self-check their understanding, ask it interactively via AskUserQuestion, then auto-grade with a table showing the user's picks plus explanations for wrong answers. Use when the user asks to verify/check their understanding of recent work ("이번 작업 내용 확인할 수 있게 퀴즈 만들어줘", "퀴즈 만들어줘", "이해도 확인", "작업 내용 퀴즈").
---

# Quiz

Generate a self-check multiple-choice quiz about the user's current work so they can verify they actually understood what changed — not a code review, not a to-do list.

## Steps

1. **Determine scope.**
   - Prefer uncommitted changes: `git status` + `git diff` for unstaged, and check staged changes too. Include untracked files that are part of the change (read them directly — they won't show up in `git diff`).
   - If nothing is uncommitted, fall back to the most recent commit (`git log -1 -p` / `git show HEAD`).

2. **Understand the change, not just the diff text.** Trace what actually changed *behaviorally/semantically* — read full files the diff touches when the diff hunks alone don't explain the intent (renamed logic, moved responsibility, changed dedup/calculation rules, new dependencies and what problem they solve, dead code left behind, etc.).

3. **Design 3–10 questions**, scaled to the size/complexity of the change (small fix → 3-4 questions; multi-file refactor → 7-10). Each question:
   - 4 options, one correct.
   - Tests understanding of *what actually changed and why*, not trivia or naming.
   - Good question shapes: a semantic/behavior change (not just a rename), an edge case, logic that was removed vs. moved vs. replaced, a new dependency and the problem it solves, and at least one "trap" option that sounds plausible but misdescribes the change (tests careful reading, not guessing).

4. **Ask via `AskUserQuestion`**, batched in groups of ≤4 questions per call (its hard limit) — never render the quiz as plain chat text with a Q1/Q2 list.
   - Do not leak the correct answer through option order, wording, or "(Recommended)" tags. Keep phrasing neutral across all 4 options.
   - Actively randomize which slot (1st–4th) holds the correct option for each question — don't just leave it wherever it landed while drafting (the correct explanation is usually written first, which silently biases it toward slot 1). Before sending each batch, check the slot distribution across that batch's questions and shuffle any that cluster.

5. **After every question is answered, grade automatically** — this is the default behavior, not something the user needs to ask for:
   - A markdown table: `문항 | 내가 선택한 답 | 정답 여부 | 정답`
   - A one-line bold summary count, e.g. "N문항 중 M개 정답"
   - A "오답 보충 설명" section at the end, one entry per wrong answer, explaining the real behavior with a concrete reference (file, method, or the actual mechanism) — not a restatement of the option text. Skip this section (or note briefly there's nothing to add) if everything was correct.

## Notes

- All quiz text — questions, options, grading table, explanations — must be in Korean.
- This skill only quizzes and grades; it never edits code, stages, or commits as part of running it.
