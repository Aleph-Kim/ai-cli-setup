---
name: artifact-style
description: The user's fixed component library for Artifact pages (Korean reading column, card sections, red-orange accent, Do Hyeon headings, 1-minute summary box, folded details, searchable card catalog). Pages are written as JSON and built with build.py, never hand-written HTML. Load before writing any new untyped HTML page to publish with the Artifact tool, in any project, such as a summary, explainer, report, guide, notes or tool catalog. Skip it when the user names another look, when another skill brings its own design (eli5, diagram-design, hallmark when named), for typed Artifacts (Docs, Slides, Sheets, Design, Data, Whiteboard), and when editing an existing artifact that already has its own design.
---

# Artifact Style

새 아티팩트 페이지는 HTML을 직접 쓰지 않고 페이지 JSON을 써서 `build.py`로 생성. 빌드가 컴포넌트 종류, 항목 이름, 개수, 글자 수를 검사하고 통과한 경우에만 HTML 생성. 아티팩트 기본 디자인 안내의 "주제마다 새 팔레트와 글꼴 고르기"보다 이 라이브러리가 우선.

## 기준 페이지

- 문서형: https://claude.ai/artifact/Uf3UyUXXGnm5Ck8ZNYYT66
- 목록형: https://claude.ai/artifact/2vViLLKExNfePCwyaTXfcV
- 두 페이지의 내용은 쓰지 않고 디자인만 참고

## 대상 정하기

새 페이지를 만들 때마다 페이지 JSON을 쓰기 전에 AskUserQuestion(Codex는 request_user_input)으로 대상을 질문하고 답을 받은 뒤 시작. 사용자가 요청에서 대상을 말했어도 생략하지 않음. 선택지는 「나만 보기」(`self`)와 「링크만 공유받은 사람」(`shared`) 두 개, 고른 값을 페이지 JSON의 `audience`에 적음 (빠지면 빌드 실패). 이미 만든 페이지를 고쳐 다시 빌드할 때는 JSON에 적힌 대상을 사용.

| audience | 읽는 사람 | 쓰는 법 |
|---|---|---|
| `self` | 대화 맥락을 아는 사용자 본인 | 사용자 프로젝트, 상황, 할 일을 직접 언급 가능. `intro` 선택 |
| `shared` | 대화를 모르고 링크만 받은 사람 | 아래 규칙 적용. `intro` 필수 |

`shared` 규칙
- `intro`(120자)에 무슨 문서인지, 누가 읽으면 좋은지, 어디서 온 내용인지를 처음 보는 사람 기준으로 설명. 핵심 용어는 처음 나올 때 괄호로 풀이
- 단락은 독자가 얻을 내용 기준으로 구성. 자료 소개("어떤 영상인가요?"), 작업 경위, 분석 방법 같은 메타 단락은 만들지 않고 출처는 `footer`나 `note`로
- 대화 안에서만 통하는 지칭 금지: "영상 1", "아까 그", "이 프로젝트", "나랑 닮은 점", "당신" 대신 발표자 이름이나 자료 이름으로
- 사용자 개인 프로젝트, 계정, 개인 정보 언급 금지
- 게시 뒤 사용자에게 공유 메뉴에서 공개해야 다른 사람이 볼 수 있다고 안내

## 작업 순서

1. `examples/doc.json`(문서형) 또는 `examples/catalog.json`(목록형)을 읽고 같은 모양으로 페이지 JSON 작성. 저장 위치는 사용자가 정하지 않았으면 스크래치패드
2. `python3 -I <이 폴더>/build.py page.json -o page.html` 실행
3. 오류가 나오면 JSON을 고쳐 다시 빌드. 글자 수 초과는 줄이거나 `details`로 접기
4. 생성된 HTML을 그대로 Artifact 도구로 게시. 생성된 HTML은 손으로 고치지 않고, 고칠 때도 JSON을 고쳐 다시 빌드
5. 게시 전 빌드 결과에 `<meta name="artifact-style">`이 있는지 확인

## 글 안 표기

모든 글 항목은 HTML을 이스케이프하고 아래 표기만 변환. 다른 HTML 태그는 글자로 표시됨.

| 표기 | 결과 |
|---|---|
| `**굵게**` | 굵은 글씨 |
| `==형광펜==` | 노란 형광펜 (단락당 1~2개) |
| `__밑줄__` | 밑줄 |
| `` `코드` `` | 코드 글씨 |
| `[글자](https://주소)` | 새 탭 링크 (http, https만) |

## 문서형 (`"layout": "doc"`)

페이지: `audience`, `intro`(shared 필수 120자, 큰 제목 아래 소개 문단), `title`(20자, 탭 이름), `eyebrow`, `h1`(30자), `lead`(선택), `hero`, `sections`(1~10개), `footer`(1~4줄, 출처와 확인 못 한 내용)

- `hero`: 1분 요약 빨간 상자. `items` 3~4개(50자), `text`(선택 160자), `eyebrow`(선택)
- `sections[]`: `id`(영어 소문자 주소), `nav`(바로가기 칩 10자), `eyebrow`(30자), `title`(40자), `blocks`(1~7개)
- 단락 바깥에는 `answer`와 `text`가 각각 1개까지, 나머지는 `details`로 접기

| type | 쓰는 곳 | 항목과 제한 |
|---|---|---|
| `answer` | 단락의 큰 답 한 줄 | `text` 120자 |
| `text` | 짧은 문단 | `text` 220자 |
| `note` | 회색 보충 문단 (출처, 단서, 주의 한마디) | `text` 200자 |
| `meter` | 비율 막대 (전체 중 일부) | `percent` 0~100 / `label` 60자 |
| `points` | 빨간 점 목록 | `items` 1~3개 100자 (details 안은 8개 200자) |
| `box` | 경고, 교훈, 좋은 소식 | `tone` red, warn, good / `title` 30자 / `text` 200자 |
| `details` | 「더 보기」 접기 | `summary` 60자 / `blocks` 1~6개 (details 중첩 금지) |
| `nums` | 큰 숫자 칸 | `items` 2~4개 {`value` 14자, `label` 60자} |
| `steps` | 동그란 번호 단계 | `items` 2~6개 140자 |
| `formula` | 개념 카드 나열 | `items` 2~4개 {`title` 12자, `text` 120자} |
| `table` | 비교표 | `columns` 2~5개 20자 / `rows` 1~30줄, 칸은 글자(120자) 또는 {`tag` ok, chk, no / `text` 16자 / `note` 선택} |
| `rank` | 숫자 붙은 순위 목록 | `items` 2~10개 {`value` 10자, `text` 120자} |
| `code` | 명령어, 설정 예시 | `text` 30줄 이하 |
| `checklist` | 체크하는 할 일 | `items` 1~5개 100자 (체크 상태는 브라우저에 저장) |
| `copy` | 복사 버튼 달린 문장 | `items` 1~10개 {`label` 40자, `text` 300자} |

## 목록형 (`"layout": "catalog"`)

여러 항목을 검색해서 찾는 페이지(도구 모음, 카탈로그). 페이지: `audience`, `intro`(shared 필수), `title`, `h1`, `eyebrow`(선택), `lead`(선택), `search`(선택, 검색창 안내), `summary` 2~4개 {`value`, `label`}, `groups` 1~20개 {`title`, `cards` 1~60개}, `footer`

- 카드: `name`(40자), `one`(한 줄 설명 120자), `badges` 0~5개 {`text` 16자, `tone` accent, line, ok, warn, new}, `info` 0~6줄 [이름 6자, 내용 160자], `links` 0~4개 {`text`, `url`}
- 검색창이 카드 글자 전체를 찾고, 결과 없는 묶음은 숨김

## 컴포넌트 추가

위 컴포넌트로 표현이 안 될 때만 추가. 페이지 HTML에 직접 넣거나 다른 컴포넌트를 억지로 변형하지 않음.

1. 표에서 대신 쓸 컴포넌트가 정말 없는지 확인 (예: 순위는 `rank`, 비교는 `table`)
2. `style.css`에 모양 추가
   - 색은 `:root` 토큰만 사용, 새 색, 새 글꼴, 그림자 금지 (다크 모드는 토큰으로 자동 대응)
   - 바깥 상자는 모서리 12~14px, 안쪽 칸은 10~12px, 테두리는 1px `var(--line)`
   - 간격은 `gap` 8, 10, 12, 16px, 큰 숫자와 짧은 제목은 `var(--display)`
   - 강조색은 컴포넌트마다 한 곳만, 휴대폰 폭(400px)에서 한 줄로 쌓이게 `auto-fit` 격자나 `overflow-x:auto` 상자 사용
3. `build.py`에 `b_<이름>` 함수 추가 후 `BLOCKS`에 등록 (카드형 목록 부품이면 `card`에 항목 추가)
   - `keys`로 허용 항목 고정, `items`로 개수 제한, 모든 글은 `text`로 글자 수 제한과 이스케이프
   - 스크립트가 필요하면 `SCRIPTS`에 추가하고 `ctx["scripts"]`로 쓸 때만 포함
4. 이 문서 표에 한 줄 추가, `examples/`의 견본 JSON에 사용 예 추가
5. 두 견본을 모두 빌드해서 오류 없이 HTML이 나오는지 확인

## 글쓰기

- 읽는 사람 기준 고등학교 1학년 수준의 쉬운 말, 전문 용어는 괄호로 풀이
- 문장은 짧게, 존댓말 "~해요"체
- 확인 못 한 숫자와 주장은 해당 단락이나 `footer`에 그 사실을 표시
- 페이지가 다루는 소재(채널, 영상, 글, 저장소, 제품, 문서)는 첫 단락에 원본 주소를 `[이름](https://주소)` 링크로 넣고, 개별 영상이나 글을 언급할 때도 링크로 표시
