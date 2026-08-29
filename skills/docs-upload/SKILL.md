---
name: docs-upload
description: eli5 스킬 결과물 또는 완성된 단일 HTML 시각화 문서를 docs 아카이브 서버에 업로드하고 등록한다. 사용자가 /docs-upload, "eli5 결과물 업로드해줘", "docs에 올려줘", "문서 업로드해줘", "시각화 결과물 등록해줘" 등의 요청을 했을 때 사용한다.
---

# docs-upload — Docs 아카이브 서버 업로더

`eli5` 스킬로 생성된 단계별 재생기 HTML 문서(또는 일반 단일 HTML 시각화 파일)를 개인 아카이브 서버(`docs`)에 업로드하여 등록합니다.
업로드 전 서버의 **카테고리 목록을 먼저 조회**하여 어울리는 카테고리를 자동 매칭하고, 필요한 경우 **새 카테고리를 자동 생성**하여 등록합니다.

---

## 1. 동작 순서

### 1-1. 업로드 대상 파일 확인
1. **eli5 직후 업로드 요청인 경우**: `/tmp/eli5-build/out.html`을 기본 대상으로 사용합니다.
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

카테고리는 개별 문서 제목이 아닌 **상위 대분류(Domain)** 체계로 관리됩니다:
- **웹/프론트엔드**: CSS, HTML, DOM, 브라우저 렌더링, JavaScript/TypeScript, React 등
- **네트워크/통신**: 웹소켓, HTTP, TCP/IP, Web Push, OAuth/인증 등
- **소프트웨어 아키텍처**: 헥사고날, 클린 아키텍처, DDD, 디자인 패턴, API 설계 등
- **데이터베이스**: SQL, NoSQL, 인덱스, 트랜잭션, ORM, Redis 등
- **인프라/DevOps**: Docker, Kubernetes, CI/CD, Linux, 클라우드 등
- **인공지능/머신러닝**: LLM, 딥러닝, 신경망, Transformer, 프롬프트 엔지니어링 등
- **컴퓨터 사이언스**: 운영체제, 프로세스/스레드, 메모리, 자료구조/알고리즘 등
- **기타 새로운 분야 (예: 생명공학/바이오, 자연과학, 금융/경제 등)**: 기존 IT 개발 분류를 벗어나는 새로운 주제의 경우, 에이전트가 해당 분야의 적절한 **상위 대분류명(예: `생명공학`, `자연과학` 등)**을 판단하여 `--category` 인자로 전달하고 새 대분류를 자동 생성합니다.

**카테고리 처리 순서**:
1. `GET /admin/categories`: 서버에 등록된 기존 카테고리 목록을 조회합니다.
2. 문서 주제와 내용을 분석하여 적합한 **상위 대분류 카테고리**를 매칭합니다. (무관한 `test` 등의 임시 카테고리는 자동 배제)
3. 기존 목록에 적합한 카테고리가 없다면 상위 대분류 카테고리를 `POST /admin/categories`로 **자동 생성**합니다.
4. 사용자가 `--category "카테고리명"`으로 직접 전달한 경우 해당 카테고리를 최우선 사용(또는 생성)합니다.
5. `POST /admin/visuals`: 결정된 카테고리와 함께 문서를 최종 등록합니다.

```bash
# 기본 실행 (자동 상위 카테고리 분류 및 등록)
python3 <스킬경로>/scripts/upload.py \
  --file /tmp/eli5-build/out.html

# 필요 시 카테고리 명시 지정
python3 <스킬경로>/scripts/upload.py \
  --file /tmp/eli5-build/out.html \
  --category "웹/프론트엔드"
```

#### 옵션 (필요 시 지정):
- `--category "카테고리명"`: 카테고리 강제 지정 (존재하지 않으면 자동 생성)
- `--title "제목"`: 제목 수동 지정 (생략 시 HTML `<title>`에서 자동 추출)
- `--description "설명"`: 설명 수동 지정 (생략 시 eli5 `<p class="one">`에서 자동 추출)
- `--slug "url-slug"`: URL 슬러그 지정 (생략 시 제목 기반 자동 생성)
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
