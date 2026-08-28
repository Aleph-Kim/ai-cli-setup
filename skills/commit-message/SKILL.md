---
name: commit-message
description: Draft a git commit message using the user's fixed personal template (Korean, single-line `type: 제목`, no body) — the same template for every repository, not repo-specific detection. Use when the user asks to write, draft, or suggest a commit message ("커밋 메시지 만들어줘/작성해줘/제안해줘"). Drafts only — never runs git commit unless the user explicitly says to commit.
---

# Commit Message

Draft a commit message for the current changes using the user's fixed personal template below. This template is the same across all of the user's repositories — do not detect or adapt to a given repo's own history/style.

**Personal template:**
- Format: `type: 한글 제목` — single line, no body, no bullets, no trailing period.
- Type vocabulary, most-used first: `feat` (new feature), `fix` (bug fix), `refactor` (restructuring without behavior change), `chore` (misc/config/deps), `design` (styling/UI-only changes), `ci` (CI/CD config). Pick whichever fits the diff; don't invent other types.
- Title in Korean, descriptive noun-phrase style (not a full sentence, no trailing "~합니다"), e.g. `fix: 관리자 수강 정보 상세 화면 데이터 표시 오류 수정`, `feat: 사용자 정보 반환 시 수강 비밀번호 설정 여부 필드 추가`.
- Keep the title short and high-level — name the target and what changed, then stop. Leave out implementation specifics ("드래그와 동일하게", "…을 통해"), comparisons, secondary qualifiers, and the why/how. Aim for roughly the length of the examples above.
- Use plain everyday verbs: 추가 / 수정 / 변경 / 삭제 / 정리. Avoid showier synonyms like 전환·도입.
- Drop the object particle (을/를) when the title reads naturally as a noun phrase: `… 이동 버튼 비동기 방식으로 변경`, not `… 이동 버튼을 … 방식으로 변경`.
- Use the user's own domain vocabulary — e.g. the list screen of an admin CRUD entity is "리스트페이지", not "목록".
- Calibration (same diff, both valid `type`): good — `refactor: 관리자 리스트페이지 순서 이동 버튼 비동기 방식으로 변경`; too verbose — `refactor: 관리자 목록 순서 이동 버튼을 드래그와 동일한 비동기 저장 방식으로 전환`.

## Steps

1. **See what changed.**
   - `git status` to see staged/unstaged/untracked files.
   - `git diff --staged` for staged changes. If nothing is staged, use `git diff` for unstaged changes instead, and mention in your reply that nothing is staged yet.
   - If both are empty, say so and stop — there's nothing to draft a message for.

2. **Draft ONE message matching the personal template above**, based on the real diff — describe what actually changed, don't guess.

3. **Present the drafted message and stop.**
   - Drafting a message is not a request to commit. Do not run `git commit`, and do not stage files, even if the message looks final.
   - Only proceed to commit if the user explicitly follows up asking to commit (e.g. "이 메시지로 커밋해줘").
