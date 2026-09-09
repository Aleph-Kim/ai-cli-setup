---
name: docs-upload
description: eli5 스킬 결과물 또는 완성된 단일 HTML 시각화 문서를 docs 아카이브 서버에 업로드하고 등록한다. 사용자가 /docs-upload, "eli5 결과물 업로드해줘", "docs에 올려줘", "문서 업로드해줘", "시각화 결과물 등록해줘" 등의 요청을 했을 때 사용한다.
---

# docs-upload — Docs 아카이브 서버 업로더

`eli5` 스킬로 생성된 단계별 재생기 HTML 문서(또는 일반 단일 HTML 시각화 파일)를 개인 아카이브 서버(`docs`)에 업로드하여 등록합니다.
업로드 전 서버의 **카테고리 목록을 먼저 조회**하여 어울리는 카테고리를 자동 매칭하고, 필요한 경우 **새 카테고리를 자동 생성**하여 등록합니다.

---

## 0. 외부 프로젝트 탐색 엄격 금지 (Strict Isolation)

- `docs-upload` 스킬은 순수한 독립 클라이언트 유틸리티입니다. 업로드에 필요한 모든 정보는 대상 HTML 파일, 스킬 디렉토리 내부의 `.env`(`DOCS_URL`, `DOCS_PASSWORD`), 에이전트가 자체 생성하는 `--slug` 및 `--category`만으로 완결됩니다.
- **로컬 머신의 다른 프로젝트 디렉토리, docs 서버 소스코드, Docker 컨테이너, DB 설정 파일 등을 검색하거나 조회하지 않습니다.**
- 서버 접속 오류나 인증 실패가 발생할 경우, 다른 코드를 분석하려 하지 말고 사용자에게 `.env` 설정(서버 주소, 비밀번호) 확인을 안내한 뒤 즉시 멈춥니다.

---

## 1. 동작 순서

### 1-1. 업로드 대상 파일 확인
1. **eli5 직후 업로드 요청인 경우**: 직전 eli5 작업에서 생성된 `/tmp/eli5-build/<slug>.html`(또는 가장 최근에 수정된 `/tmp/eli5-build/*.html`)을 기본 대상으로 사용합니다.
2. **사용자가 특정 경로를 지정한 경우**: 해당 파일 경로를 사용합니다.
3. 대상 파일이 없거나 불분명하면 업로드할 파일 경로를 사용자에게 확인합니다.

### 1-2. 환경 설정 (.env) 확인
스킬 폴더 내부의 `.env` 파일(`skills/docs-upload/.env`)에서 서버 접속 정보를 읽습니다:

```dotenv
DOCS_URL=http://localhost:8000
DOCS_PASSWORD=서버_관리자_비밀번호_또는_API키
```

- `DOCS_PASSWORD`가 비어있으면 사용자에게 `.env` 파일에 비밀번호 설정을 안내합니다.

### 1-3. 카테고리 매칭 및 업로드 실행

카테고리는 개별 문서 제목이 아닌 **상위 대분류(Domain)** 체계로 관리되며, `eli5` 스킬의 분류표(`skills/eli5/scripts/build.py`)와 이름을 맞춥니다. `upload.py`의 `DOMAIN_TAXONOMY`가 그 사본이며 수동 동기화합니다:
- **웹/프론트엔드**: CSS, HTML, DOM, 브라우저 렌더링, JavaScript/TypeScript, React 등
- **네트워크/통신**: 웹소켓, HTTP, TCP/IP, Web Push, REST/gRPC, DNS, CDN 등
- **보안**: 인증/인가, OAuth, JWT, 암호화, 세션/쿠키, CORS/CSRF/XSS 등
- **소프트웨어 아키텍처**: 헥사고날, 클린 아키텍처, DDD, 디자인 패턴, 메시지 큐, CQRS 등
- **데이터베이스**: SQL, NoSQL, 인덱스, 트랜잭션, ORM, Redis, 샤딩 등
- **인프라/DevOps**: Docker, Kubernetes, CI/CD, Linux, 클라우드 등
- **컴퓨터 사이언스**: 자료구조/알고리즘, 운영체제, 프로세스/스레드, 메모리, 컴파일러, 테스트/디버깅 등
- **인공지능/머신러닝**: LLM, 딥러닝, 신경망, Transformer, 프롬프트 엔지니어링, RAG 등
- **자연과학**: 물리, 화학, 우주, 생물, 지구/기후 등
- **의학/생명**: 인체, 면역, 세포, 바이러스/백신, 생명공학 등
- **경제/금융**: 금리, 환율, 주식, 투자, 부동산 등
- **인문/사회**: 역사, 철학, 정치, 법, 예술 등

위 목록에 없는 새로운 분야는 에이전트가 적절한 상위 대분류명을 판단해 `--category`로 전달하고 새 대분류를 자동 생성합니다. `eli5` 산출물을 올릴 때는 `build.py`가 출력한 `상위 대분류: ...` 값을 그대로 `--category`로 넘깁니다.

**서버 카테고리 색상**: 각 카테고리의 색상은 `eli5`의 대표 악센트 색상과 일치시킵니다. 표준 색상 목록은 `python3 skills/eli5/scripts/build.py --categories` 로 출력합니다(`색상<TAB>대분류` 형식). 한 대분류가 여러 색을 쓰는 경우(컴퓨터 사이언스·자연과학) 카테고리 배지는 대표색 하나만 사용합니다.

**카테고리 처리 순서**:
1. `GET /admin/categories`: 서버에 등록된 기존 카테고리 목록을 조회합니다.
2. 문서 주제와 내용을 분석하여 적합한 **상위 대분류 카테고리**를 매칭합니다. (무관한 `test` 등의 임시 카테고리는 자동 배제)
3. 기존 목록에 적합한 카테고리가 없다면 상위 대분류 카테고리를 `POST /admin/categories`로 **자동 생성**합니다.
4. 사용자가 `--category "카테고리명"`으로 직접 전달한 경우 해당 카테고리를 최우선 사용(또는 생성)합니다.
5. `POST /admin/visuals`: 결정된 카테고리와 함께 문서를 최종 등록합니다.

### 1-4. 슬러그(URL Slug) 자동 생성 (필수)
- **슬러그 생성 원칙**: 에이전트는 문서 주제와 내용을 파악하여 **반드시 의미 있고 명확한 영문 kebab-case 슬러그(예: `watch-app-languages`, `hexagonal-architecture`, `vue-reactivity-system` 등)를 스스로 생성**하여 `--slug` 인자로 전달합니다.
- 한글 제목의 경우 서버에서 비-ASCII 문자가 제거되어 무작위 8자리 난수 해시(예: `r0runxso`)로 폴백되므로, **에이전트는 `--slug` 인자를 절대로 생략하지 않고 항상 직접 생성하여 전달**합니다.

```bash
# 기본 실행 (에이전트가 생성한 영문 슬러그 전달 또는 파일명의 슬러그 활용)
python3 <스킬경로>/scripts/upload.py \
  --file /tmp/eli5-build/watch-app-dev-languages.html \
  --slug "watch-app-dev-languages"

# 필요 시 카테고리 명시 지정
python3 <스킬경로>/scripts/upload.py \
  --file /tmp/eli5-build/watch-app-dev-languages.html \
  --slug "watch-app-dev-languages" \
  --category "웹/프론트엔드"
```

#### 옵션:
- `--slug "url-slug"`: **(필수 전달)** 에이전트가 문서 주제를 분석하여 생성한 영문 kebab-case 슬러그
- `--category "카테고리명"`: 카테고리 강제 지정 (생략 시 상위 대분류 자동 매칭/생성)
- `--title "제목"`: 제목 수동 지정 (생략 시 HTML `<title>`에서 자동 추출)
- `--description "설명"`: 설명 수동 지정 (생략 시 eli5 `<p class="one">`에서 자동 추출)
- `--url "http://..."`: 서버 URL 오버라이드
- `--key "비밀번호"`: 비밀번호 오버라이드

---

## 2. 응답 전달

스크립트 실행이 성공하면 반환된 상세 페이지 URL과 렌더링 URL을 사용자에게 마크다운 링크로 깔끔하게 안내합니다:

> **문서 등록이 완료되었습니다.**
> - **문서명**: 헥사고날 아키텍처
> - **카테고리**: 인터랙티브
> - **상세 페이지**: [DOCS_URL/visuals/hegsagonal-akitegceo](DOCS_URL/visuals/hegsagonal-akitegceo)
> - **전체화면 렌더링**: [DOCS_URL/visuals/hegsagonal-akitegceo/render](DOCS_URL/visuals/hegsagonal-akitegceo/render)
