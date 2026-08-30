# 디자인 프리셋 — 미니멀 문서형 + 도트 폰트

사용자가 라운드 3에서 이 프리셋을 골랐을 때만 쓴다. 아래 내용을 프롬프트의 `## 디자인 요구사항` 절에 옮긴다. 프로젝트 성격에 따라 최대 폭이나 카드 형태는 조정해도 되지만 **폰트 블록과 색상 토큰은 값 그대로 옮긴다.** 임의로 색을 바꾸면 사용자가 쌓아온 톤이 어긋난다.

---

**폰트** — 둥근모꼴+ Fixedsys (한글은 둥근모꼴, 영문·숫자는 Fixedsys가 합쳐진 단일 폰트, 퍼블릭 도메인):

```css
@font-face {
  font-family: 'DungGeunMo';
  src: url('https://cdn.jsdelivr.net/gh/projectnoonnu/noonfonts_six@1.2/DungGeunMo.woff') format('woff');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}
```

- 전역 `font-family: 'DungGeunMo', ui-monospace, Menlo, Consolas, monospace;`
- 도트 폰트는 힌팅이 없으므로 `-webkit-font-smoothing: none;` 과 짝수 `font-size`(12px / 14px / 16px / 20px)를 사용해 픽셀이 뭉개지지 않게 한다

**색상 토큰** — `:root` 변수로 정의:

```
--bg:#ffffff  --card:#fafafa  --line:#e4e4e7  --line-2:#d4d4d8
--ink:#18181b --ink-2:#3f3f46 --ink-3:#71717a --ink-4:#a1a1aa
--accent:#0f766e --accent-soft:#d7f2ee
```

**레이아웃**

- 최대 폭 1100px 중앙 정렬
- 상단 헤더: 좌측 사이트명(대문자 + letter-spacing), 우측 기능 링크
- 카드: `1px solid var(--line)`, `border-radius: 6px`, hover 시 테두리만 accent로 변경 (그림자·트랜스폼 금지)
- 버튼: 4px 라운드, 배경 `--card`, 테두리 `--line-2`
- 필터는 상단 가로 칩(chip) 형태
- 여백 위주의 미니멀 문서형 레이아웃. 장식 요소를 넣지 않는다

**CSS 작성 방식**

- Tailwind를 쓰지 않는다. 프레임워크 스켈레톤에 Tailwind import가 들어있으면 제거하고 순수 CSS로 직접 작성한다. `package.json` 의 Tailwind 의존성도 제거한다
- 빌드 도구는 기본 설정을 그대로 쓴다

---

## 외부 HTML을 iframe으로 품는 프로젝트일 때 추가

저장된 HTML이 완결 문서인 경우에만 해당한다.

- iframe 내부는 원본 스타일을 그대로 유지한다. 폰트를 강제 적용하지 않는다
- 원문만 반환하는 별도 라우트를 두고 iframe의 `src` 로 불러온다. 레이아웃 안에 직접 출력하면 CSS·JS가 충돌한다
- `sandbox="allow-scripts allow-popups"` 를 적용하고 `allow-same-origin` 은 넣지 않는다 (같이 넣으면 샌드박스가 무력화됨). 이 조합에서 인라인 스크립트와 외부 CDN은 동작하지만 localStorage 계열은 차단된다
- iframe 높이 자동 조절은 저장된 HTML을 고쳐야 가능하므로 시도하지 않는다. 고정 높이 + 전체화면 토글 버튼으로 처리한다
