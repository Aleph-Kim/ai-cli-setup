# claude-skills

개인 Claude Code 스킬을 보관하고, 다른 개발 환경으로 쉽게 이식하기 위한 레포입니다.

## 포함된 스킬

- `comment-style` — 코드 주석을 개인 고유 스타일(한글, WHY 중심)로 작성
- `commit-message` — 커밋 메시지를 개인 고유 템플릿(`type: 한글 제목`)으로 초안 작성
- `quiz` — 작업 내용 이해도 확인용 4지선다 퀴즈 생성
- `task-observer` — 세션 중 작업을 관찰해 스킬 개선/신규 스킬 후보를 기록하는 메타 스킬 (rebelytics/one-skill-to-rule-them-all, CC BY 4.0)

## 설치 (다른 환경으로 이식)

```bash
git clone <this-repo-url>
cd claude-skills
./install.sh
```

`skills/` 하위의 각 스킬 디렉토리를 `~/.claude/skills/`에 심볼릭 링크로 연결합니다. 레포가 항상 원본이므로, 이후 스킬을 수정하면 레포에서 바로 반영됩니다.

대상 디렉토리를 바꾸려면 인자로 지정하세요:

```bash
./install.sh /path/to/skills
```

## 새 스킬 추가

`skills/` 아래에 스킬 폴더(SKILL.md 포함)를 추가하고 `./install.sh`를 다시 실행하면 됩니다.
