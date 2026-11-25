---
name: result-check
description: >
  Manually invoked only (`/result-check [target]`) — do not trigger automatically.
  Check that something made or changed with AI produced the wanted result:
  compare the before and after states of whatever was made or changed (code,
  documents, specs, translations, data, settings, prompts, skills, messages,
  images), confirm every wanted change is present and nothing unrequested
  changed, back each claim with evidence from both states, and report per item
  whether the after result matches what was wanted.
disable-model-invocation: true
---

# Result Check

Proves a change does what was wanted, not just that the after state looks fine.
A check that would also pass on the before state proves nothing about the change.

## Target

Default target: the changes made in the current session. If the user names a
target (files, a document, a commit range, a data set), check only that. If it
is unclear what changed or what the before state is, ask before step 1.

## Steps

1. **Write the wanted results.** One line per wanted change, each quoting the
   user's request or the spec line it comes from, with one concrete example:
   an input or location, and the output wanted there. A line with no such
   source is marked 추정. Show the list. If any line is 추정 or its wanted
   output is vague ("자연스럽게", "정리"), propose one concrete example and
   wait for agreement; otherwise continue.

2. **Secure the before state.** Get the real before state, not a recollection
   of it: version history (git, document revisions), a backup or original
   copy, the original text still visible in the conversation. Name the source
   of the before state in the report.
   - Newly created thing (new message, translation, image, file): the before
     state is "did not exist". Compare the after state against step 1 and
     against the source material it was made from.
   - Before state existed but cannot be recovered, or only in part: say which
     part; those items can only be 확인 못 함.

3. **Diff before and after.** Produce the differences with a tool where the
   medium has one (git diff, diff, cell-by-cell compare), not from memory of
   what was edited. Where a full diff is not possible (images, very large
   data), state the method and what was compared. Sort each difference into:
   - wanted: traces to a line from step 1
   - side effect: not requested (reformatting, reworded text, moved items,
     removed content, changed numbers, files touched outside the target)
   - missing: a wanted line with no matching difference

4. **Block outside effects before running anything.** Read the path the check
   will exercise for anything that reaches outside (sending mail or messages,
   payments, external APIs, posting, publishing, overwriting shared files) and
   confirm each is blocked or faked. If that cannot be confirmed, do not run
   it; mark the item 확인 못 함. Ask before driving a browser.

5. **Gather evidence for each wanted line, in both states.** Use the strongest
   evidence the medium allows, and run the same check on before and after:
   - executable things (code, scripts, formulas, queries, settings): run the
     new check against the old version of the thing being checked. Revert
     only the changed target, keep the check itself. The before run must fail
     or differ for the expected reason (if the wanted result is "no change",
     before and after must match); capture the actual output or error.
   - prompts, skills, instructions: run them on the same sample input before
     and after, compare outputs against step 1.
   - documents, translations, messages: quote the before and after passages
     for each item; check meaning is preserved where nothing was meant to
     change, and check the facts against the source.
   - data and numbers: recompute totals, counts or samples independently from
     the source, compare before and after values.
   - visual output: render or open both versions and compare.

   Prefer running the before version in a separate copy. If the working state
   must be swapped in place, record it first (file list plus a saved diff or
   copy), restore it after, and show that the record matches again.

6. **Name what the evidence does not cover.** A sample that skips edge cases,
   a preview that differs from the real renderer or recipient's view, a test
   setup that differs from real use. List each gap; verify it for real only
   with the user's agreement.

7. **Report.**

   First line: one-sentence conclusion (원한 결과가 맞는지, 몇 개 중 몇 개).

   | 원한 것 | 전 | 후 | 판정 |
   |---|---|---|---|
   | (step 1 line) | (actual before result + 근거) | (actual after result + 근거) | 맞음 / 다름 / 확인 못 함 |

   근거 is one of: 실행 (the command and its output), 인용 (the passage and
   where it is), 기억 (not re-read or re-run in this check). A row with 기억
   in either cell is 확인 못 함.

   Then list: side effects from step 3, gaps from step 6. Never mark an item
   맞음 when a before state existed and was not checked. Do not fix side
   effects or mismatches on your own; propose and wait.
