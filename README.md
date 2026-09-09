# ai-cli-setup

개인 AI 코딩 환경(Claude Code, AGY CLI)의 전역 규칙(Rules), 상태표시줄(Statusline), 스킬(Skills)을 통합 보관하고 새 환경에 안전하게 배포하기 위한 저장소입니다.

## 구성

### 1. Rules (`rules/`)
AI 에이전트의 공통 행동 지침 및 원칙을 단일 원본 파일로 관리합니다.
- 원본: `rules/RULES.md`
- 배포: `~/.claude/CLAUDE.md` 및 `~/.gemini/GEMINI.md`로 심볼릭 링크 연결
- Think Before Coding, Simplicity First, Surgical Changes, 한국어 응답 원칙 등 포함

### 2. Statusline (`statusline/`)
터미널 하단에 모델명, Quota(5시간/주간 사용량 및 리셋 시각) 등을 표시하는 커스텀 상태표시줄 스크립트입니다.
- `statusline/agy-statusline.js` -> `~/.gemini/antigravity-cli/statusline.js`
- `statusline/claude-statusline.sh` -> `~/.claude/statusline.sh`

### 3. Skills (`skills/`)
- `comment-style` — 코드 주석을 개인 고유 스타일(한글, WHY 중심)로 작성
- `commit-message` — 커밋 메시지를 개인 고유 템플릿(`type: 한글 제목`)으로 초안 작성
- `quiz` — 작업 내용 이해도 확인용 4지선다 퀴즈 생성
- `eli5` — 주제를 "단계별 재생기" 형식의 인터랙티브 아티팩트로 시각화 (개념/구현 모드, 에디토리얼 SVG 다이어그램 연계)
- `diagram-design` — 39가지 시각 유형(아키텍처, 플로우차트, 시퀀스, ERD 등)의 에디토리얼 SVG 다이어그램 생성 (명시적 호출 시 작동, eli5의 다이어그램 레퍼런스로 활용)
- `docs-upload` — eli5 결과물 또는 HTML 시각화 문서를 docs 아카이브 서버에 업로드/등록
- `task-observer` — 세션 중 작업을 관찰해 스킬 개선/신규 스킬 후보를 기록하는 메타 스킬
- `project-prompt` — 프로젝트 주제 기반 기본 세팅 프롬프트 생성
- `taste-skill` — 랜딩/마케팅 페이지의 디자인 방향 결정 및 AI 특유의 템플릿 티(AI Slop) 차단
- `web-design-guidelines` — 인터랙션·폼·접근성·성능 등 프로덕션 수준 프론트엔드 품질 체크리스트 강제
- `hyperui` — HyperUI(hyperui.dev) 스타일의 순수 HTML5 + Tailwind CSS 전용 컴포넌트 마크업 가이드 (React/JSX 배제, 시맨틱 HTML 우선)
- `ponytail` — 가장 게으르고 단순한 시니어 개발자 원칙(YAGNI, 표준 라이브러리 및 네이티브 우선, 최소 코드) 강제 (`ponytail`, `ponytail-review`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`)

---

## 설치 및 배포

```bash
git clone https://github.com/Aleph-Kim/ai-cli-setup.git
cd ai-cli-setup
./install.sh
```

### 안전 장치 (백업 및 확인)
`./install.sh` 실행 시 이미 대상 경로에 일반 파일이나 다른 설정이 존재하면:
1. 기존 설정 파일 경로(`file exists: ...`)를 출력합니다.
2. `기존 파일을 백업하고 덮어쓰시겠습니까? [y/N]` 확인을 거칩니다.
3. `y` 입력 시 기존 파일은 해당 디렉토리의 `backup/` 폴더(`{dir}/backup/{file}.bak_YYYYMMDDHHMMSS`)로 백업된 뒤 심볼릭 링크로 교체됩니다. (`n` 입력 시 기존 설정 유지)
4. 이미 이 저장소의 원본을 가리키는 링크는 `already linked`로 통과합니다.

### 옵션 플래그

```bash
# 질문 없이 즉시 자동 백업 후 심볼릭 링크 적용
./install.sh -y

# 특정 카테고리만 설치
./install.sh --rules-only       # 규칙(rules)만 배포
./install.sh --statusline-only  # 상태표시줄(statusline)만 배포
./install.sh --skills-only      # 스킬(skills)만 배포
```

## 새로운 설정 또는 스킬 추가
- `rules/`: 전역 프롬프트 지침 추가 및 수정
- `statusline/`: 상태표시줄 포맷 또는 로직 수정
- `skills/`: 새 스킬 디렉토리(`SKILL.md` 포함) 추가 후 `./install.sh` 재실행
