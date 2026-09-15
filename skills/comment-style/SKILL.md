---
name: comment-style
description: Write code comments using the user's fixed personal style (Korean, WHY-focused, sparse) — the same convention across all repositories, not language/repo-specific detection. Trigger before any code edit that adds or touches comment characters (//, #, /** */, etc.), whenever writing or adding comments, or when the user asks to comment code in "my style" ("주석 스타일대로/평소처럼 달아줘", "주석 컨벤션 알려줘"). Does not apply to commit messages (see commit-message skill) or docs/markdown.
---

# Comment Style

Apply the user's fixed personal comment convention. It is a personal habit, not a project-specific rule — use it in any codebase, in whatever comment syntax that language provides (`//`, `#`, `<!-- -->`, etc.), keeping the same shape and judgment described below.

**Activation checkpoint (artefact-triggered):** Load and consult this skill before any edit that writes or touches comment lines (`//`, `#`, `/*`, `/**`, `<!-- -->`). When editing code, comments often arise incidentally rather than by explicit user prompt; treat the act of inserting or modifying a comment line as the invocation checkpoint.

## Core rules

1. **Language: always Korean.** Comment text is Korean regardless of the code's identifiers or the project's dominant language. Code itself (variable/function names, strings the app outputs, etc.) is untouched — only the comment prose is Korean.

2. **Placement: directly above the code it explains**, not trailing — except for rule 3c. One comment sits immediately before the block, statement, or method it describes.

3. **Comment shapes, chosen by placement and context.** Both end in a noun phrase (명사형 종결: "~저장", "~조회", "~폴백", "~발송", "~목록") — never a verb-ending full sentence like "~한다/~된다", even in the block form. **No trailing period** — a noun phrase doesn't take one; this holds even when a comment packs two clauses separated by a mid-sentence period (e.g. "큐에 쌓인 알림을 일괄 전송, 만료된(410/404) 구독은 자동 삭제").
   - **Passes the letter of this rule but still wrong** — no trailing period, doesn't end in a conjugated verb, and yet violates the convention:
     - No symbolic notation standing in for a verb (`=`, `→`, etc.) — spell the relationship out in Korean prose instead.
       ```php
       // 틀림: 이미 locale 접두사가 붙었는데 매칭 실패 = 진짜 404
       // 맞음: locale 접두사가 있는 경로의 404 처리 (접두사 누락으로 인한 실패와 구분)
       ```
     - The final word must be an actual nominalized noun (조회/저장/방지 류), not a bare literal value (a number, an id, a status code) tacked on as the last token — ending on "404" isn't a noun-phrase ending just because it isn't a verb.
     - Prefer one compressed noun-phrase chain over a reasoned sentence built from connective endings (`-이므로`, `-면`, `-는데도`, i.e. "since X, if Y then Z") — even when the very last word is a genuine noun, a comment shaped like a small paragraph of reasoning still reads wrong; compress it to a label like the examples in this rule.
       ```php
       // 틀림: 컨트롤러 인자는 위치 기반 바인딩이므로, locale을 남겨두면 뒤따르는 파라미터가 밀리는 문제 방지
       // 맞음: 컨트롤러 인자 위치 바인딩 특성으로 인한 뒤 파라미터(boardSlug 등) 밀림 방지
       ```
   - **(a) Single-line `//` — method body and statement blocks.** Used for statements, logic branches, and blocks inside a method or function body.
     ```php
     // 가수 조회 및 저장 (이미지 업로드는 신규 생성 시에만)
     // 큐에 쌓인 알림을 일괄 전송, 만료된(410/404) 구독은 자동 삭제
     ```
   - **(b) `/** */` doc block — ALWAYS used above method, function, and property declarations.**
     - Any comment placed directly above a method, function, or property declaration must use the doc comment syntax (`/** ... */`), regardless of whether it is a single line or multi-line:
       ```php
       /**
        * 가수 조회 및 저장 (이미지 업로드는 신규 생성 시에만)
        */
       public function findOrCreateArtist(...)

       /**
        * 멜론 검색 페이지 스크래핑으로 실제 songId 파싱 후 melonapp:// 딥링크 생성
        * 멜론 앱 스킴은 songId 기반 재생만 지원 (검색 미지원)
        */
       public function createMelonDeepLink(...)
       ```
     - `@param`, `@return` 등의 태그는 기본적으로 생략(순수 한국어 산문 우선)하되, **파라미터명이나 반환 구조만으로 직관적인 이해가 어려울 경우**에는 필요한 태그를 선별적으로 추가:
       ```php
       /**
        * 취약점 데이터를 분석하여 간결하고 자연스러운 한국어 설명 생성
        *
        * @return array{definition: string, environment: string, attack_path: string, remediation: string}
        */
       public function analyze(Vulnerability $vulnerability, ?Target $target = null): array
       ```
   - **(c) Trailing inline comment — only for a one-word/short clarification of a literal value** on the same line (e.g. a constant or a magic number).
     ```php
     private const MUSIC_CACHE_TTL = 604800; // 7일
     usleep(random_int(1_000_000, 3_000_000)); // 1~3초
     ```
   - **(d) Per-field comment above each field in `FormRequest::rules()` and API Resource arrays** — for API documentation purposes, every field gets a short `//` comment on the line above it describing what it is, noun-phrase, no period. Not trailing — same above-the-code placement as rule 2. This is separate from `FormRequest::attributes()` (which supplies Korean labels for validation error messages) — add the comment even when `attributes()` already exists.
     ```php
     public function rules(): array
     {
         return [
             // 별점 (1~5)
             'score' => ['nullable', 'integer', 'between:1,5'],
             // 코멘트
             'comment' => ['nullable', 'string'],
         ];
     }
     ```

4. **Content bias: explain WHY, not WHAT.** Never restate what the code visibly does line by line. A comment earns its place only when it captures intent, a business rule, or a constraint the reader can't get from reading the code itself. If the code is self-evident, don't comment it.

5. **Sparse by default.** Comment only at real decision points: business-logic branches, non-obvious external-system constraints, or short workarounds. Most functions and most lines carry zero comments — don't add one to every method just because you touched it.
   - **Pre-write gate, run before choosing a shape:** for each candidate comment, state what the reader loses if it is deleted. If the answer is "nothing — the name and signature already say it", don't write it. The shape rules (Korean, noun-phrase, doc block) are self-checkable from the comment text alone, so they get satisfied while this one gets skipped; that is exactly how a file ends up with a doc block above nearly every method.
   - **Concrete density test:** a file where the majority of declarations carry doc blocks is presumed wrong until each one names a constraint, decision, or non-obvious return shape.
   - Correctly withheld:
     ```php
     // 틀림 — 이름이 이미 말하는 것을 반복
     /**
      * 사용자 ID로 사용자 조회
      */
     public function findUserById(int $id): ?User

     // 맞음 — 주석 없음. 이름과 시그니처가 전부 말한다
     public function findUserById(int $id): ?User
     ```

6. **No banners, no markers, no boilerplate.** No `====`/`----`/`#region` section dividers, no `TODO`/`FIXME` tags, no file- or class-level doc comments. For `@param`/`@return`, use only when non-obvious parameter or return shape clarification is genuinely needed per rule 3b. Just the comment types in rule 3.

7. **Keep existing comments truthful.** When editing code, check nearby existing comments. If your change falsifies or alters what an existing comment asserts, update or remove that comment in the same edit — never leave a stale, misleading comment behind.

## When applying this in a non-PHP codebase

Keep the same shapes and the same judgment (noun-phrase ending, WHY/caller-context over WHAT, sparse, Korean), just swap the syntax for the language's native comment form — `//` in JS/TS/Go/Java, `#` in Python/Ruby, `<!-- -->` in HTML/blade when a block explanation is genuinely warranted. Use that language's own doc-comment block syntax for shape (b) (e.g. `/** */` in JSDoc/TSDoc, `"""..."""` in Python), adding `@param`/`@returns` tags only when type/parameter clarification is genuinely non-obvious.

## Steps

1. Read the surrounding code to find genuine WHY-worthy spots — non-obvious constraints, business rules, external-system limitations, short workarounds, or a reusable model/query-builder method whose callers are worth noting. Skip self-evident code entirely.
2. For each spot, pick shape (a)–(d) per rule 3, and write the comment in Korean following the tone in the examples above.
3. Don't add comments beyond what's asked — if the user asked to comment one function, don't sweep the whole file.
