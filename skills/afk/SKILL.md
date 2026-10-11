---
name: afk
description: >
  Manually invoked only (`/afk`) — do not trigger automatically from phrases
  like "자리 비워도 돼?". Run when the user is about to step away mid-task:
  read the remaining work now, ask every open question in one batch before
  they go, then tell them explicitly whether they can leave now, with an
  estimated duration, what will proceed unattended, and what waits for
  their return — instead of promising to "leave questions for later".
---

# AFK — Clear Blockers Before the User Leaves

The moment the user announces an absence is the last chance to ask anything. A question discovered after they leave turns their whole absence into idle waiting. So "I'll leave a question if something's unclear" is never an acceptable answer — find the questions now.

The goal is an absence with zero pause points: everything that needs the user is either resolved before they leave or moved to after their return. Nothing waits on them in between.

## Steps

1. **List the remaining work.** Every pending item in the current task — the remaining rounds, follow-up requests queued mid-turn, and anything promised earlier in the session. Don't drop items that were mentioned only in passing.

2. **Read before classifying.** For each item, open the code or files it touches and trace what the change would actually do. Classifying from the item's title alone is what misses ambiguity — a request that reads clear ("이동시키도록 변경") can already be the current behavior, or admit several targets. While reading, also record each item's work size for step 5: files to change and how much, tests to write, full test runs needed, and any long-running command (build, migration, install).

3. **Classify every item into exactly one bucket:**
   - **Ambiguous** — more than one reasonable interpretation, the requested behavior already exists, or a decision the user owns (scope, naming, UX target). → ask now.
   - **Needs the user's hands** — verification only they can do (a real device, a logged-in browser, a production console). → move to after their return, together with every item that depends on its result.
   - **Needs permission** — commands that may raise a permission prompt or are outward-facing (push, deploy, external writes, network calls outside the test fakes). → get approval before they leave; if they can't approve now, move it to after their return.
   - **Hard to reverse** — destructive or history-rewriting operations (deletes, force-push, migrations against shared DBs). → do not run unattended; move to after their return.
   - **Clear** — everything else. → proceed.

4. **Ask in one batch.** All Ambiguous items and all pending permission approvals go into one AskUserQuestion call (up to 4 questions per call; chain calls only if more remain). For each, state the current behavior you found and the concrete options — the user should be able to answer without opening any file.

5. **Estimate the time from the work itself.** Do not use a fixed per-round or per-task number — the size of a "round" differs completely between tasks. Instead, for each unattended item:
   - Start from the work size recorded in step 2 (files, tests, test runs, long commands).
   - Measure what can be measured: run the test suite once now and use its real runtime, so test cost is (number of full runs × measured runtime). In projects with slow suites this term dominates the total.
   - If items of similar size were already completed earlier in this same session, calibrate against how long they actually took (e.g. from commit timestamps: `git log --date=format:%H:%M:%S --format="%ad %s"`). If there is no comparable item, don't invent one — widen the range instead.
   - Don't estimate in human-developer time; the agent's own measured pace is the baseline.

   Sum into a range and show the basis in one line, e.g. "약 N~M분 (파일 X개 수정, 테스트 실행 K회 × 실측 S초 포함)". If a step depends on something that can't be timed (an external service, a remote build), say so separately instead of folding it into the number.

6. **Give the verdict after the answers, as the reply's first line.**
   - **떠나도 될 때** — only when no remaining unattended step can pause on the user: "이제 자리 비우셔도 됩니다. 예상 소요 시간은 약 N~M분입니다." Then list what will proceed unattended (in order, with each item's estimate) and what was moved to after their return.
   - **아직 안 될 때** — whenever anything still needs them before work can run to completion unattended: "아직은 자리를 비우시면 안 됩니다." Then name exactly what is still needed (an unanswered question, an approval) and ask for it. Re-issue the verdict once it's resolved.

## Pre-flight check (before step 6)

Re-read the bucket list and confirm:
- every remaining item was read in code, not classified by title;
- no item marked Clear depends on an unanswered decision or on a result only the user can produce;
- no unattended step can stop on a permission prompt — each was approved or moved to after return;
- the reply contains no "I'll ask later / leave a question" and no "N분 뒤 승인이 필요합니다" — either is a pause point, which means the verdict must be "아직 안 됩니다";
- the reply opens with an explicit go/no-go verdict, not a summary the user has to interpret;
- the estimate is a range with its basis shown, and every unattended item has its own estimate.

If any check fails, return to the step it violates.

## Common failure patterns

- **Promising to leave questions.** "애매하면 질문을 남겨 두겠습니다" — the exact failure this skill exists to prevent.
- **Answering "yes" first, checking later.** Saying "네, 비우셔도 됩니다" before step 3 finishes commits to an absence you haven't de-risked.
- **Saying "go" while a pause point remains.** Announcing "약 20분 뒤 승인이 필요합니다" alongside "비우셔도 됩니다" contradicts itself — resolve the approval now or move that step after their return.
- **Treating a queued mid-turn request as out of scope.** A request the user sent while you were working is remaining work — classify it like the rest.
- **Deciding an ambiguous item yourself to avoid asking.** Picking an interpretation silently (e.g. quietly dropping part of the requested behavior because it looked infeasible) is worse than asking — the user returns to work they didn't want.
- **Estimating in human time or from a fixed number.** "2시간 정도" for work the agent finishes in minutes, or reusing one task's per-round time for a different task. Estimate from the item's own work size and measured test runtime.
