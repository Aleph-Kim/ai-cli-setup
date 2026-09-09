#!/usr/bin/env python3
"""셸 템플릿에 주제 · SVG · STEPS 배열 · 악센트 색상을 주입해 최종 HTML을 만든다."""
import argparse, pathlib, re, sys

# ─────────────────────────────────────────────────────────────────────────────
# 도메인 분류표 (단일 출처)
#
# 각 항목: ("상위 대분류", "악센트 색상", [주제 키워드])
#   - "상위 대분류" 이름은 docs-upload 스킬의 카테고리 체계와 반드시 일치시킨다.
#     (skills/docs-upload/scripts/upload.py 의 DOMAIN_TAXONOMY 와 수동 동기화)
#   - 색 구분을 위해 한 대분류가 여러 규칙으로 쪼개질 수 있다 (예: 컴퓨터 사이언스).
#   - 위에서부터 첫 부분 문자열 매칭이 채택되므로, 좁은 주제를 먼저 둔다.
# ─────────────────────────────────────────────────────────────────────────────

# 개발/엔지니어링 도메인 (1차 우선 매칭)
DEV_DOMAIN_RULES = [
    (
        "보안", "#4f46e5",  # Indigo: 인증 / 인가 / 암호화 / 토큰
        [
            "auth", "oauth", "jwt", "ssl", "tls", "token", "보안", "인증", "인가",
            "암호화", "세션", "session", "쿠키", "cookie", "rbac", "cors", "csrf",
            "xss", "crypto", "secret", "비밀번호", "password", "oauth2"
        ]
    ),
    (
        "인공지능/머신러닝", "#db2777",  # Pink: LLM / 딥러닝 / 학습
        [
            "인공지능", "머신러닝", "machine learning", "딥러닝", "deep learning",
            "신경망", "neural", "llm", "gpt", "트랜스포머", "transformer", "임베딩",
            "embedding", "파인튜닝", "fine-tuning", "프롬프트", "prompt", "rag",
            "확산 모델", "diffusion", "강화학습", "reinforcement learning",
            "생성 모델", "생성형", "벡터 데이터베이스", "벡터 db"
        ]
    ),
    (
        "데이터베이스", "#059669",  # Emerald: DB / 캐시 / 저장소 / 쿼리
        [
            "db", "database", "sql", "rdbms", "nosql", "redis", "cache", "캐시",
            "postgres", "postgresql", "mysql", "mongodb", "sqlite", "인덱스", "index",
            "트랜잭션", "transaction", "orm", "jpa", "prisma", "migration", "sharding",
            "replication", "스토리지", "storage"
        ]
    ),
    (
        "인프라/DevOps", "#0891b2",  # Cyan: 클라우드 / 컨테이너 / 배포
        [
            "docker", "k8s", "kubernetes", "도커", "쿠버네티스", "aws", "gcp", "azure",
            "cloud", "클라우드", "terraform", "ci/cd", "cicd", "nginx", "컨테이너",
            "container", "배포", "deploy", "serverless", "lambda", "infra", "인프라"
        ]
    ),
    (
        "소프트웨어 아키텍처", "#d97706",  # Amber: 시스템 설계 / 메시징 / 큐
        [
            "architecture", "아키텍처", "hexagonal", "헥사고날", "clean architecture",
            "클린", "ddd", "domain driven", "kafka", "카프카", "rabbitmq", "mq",
            "queue", "큐", "event", "이벤트", "msa", "microservice", "마이크로서비스",
            "pattern", "패턴", "pub/sub", "pubsub", "saga", "cqrs"
        ]
    ),
    (
        "웹/프론트엔드", "#7c3aed",  # Violet: 웹 / UI / 렌더링
        [
            "react", "vue", "next.js", "nextjs", "svelte", "dom", "css", "html",
            "frontend", "프론트", "프론트엔드", "브라우저", "browser", "rendering",
            "렌더링", "ui", "ux", "상태관리", "redux", "zustand", "tailwind", "webpack", "vite"
        ]
    ),
    (
        "네트워크/통신", "#2563eb",  # Blue: 프로토콜 / API
        [
            "network", "네트워크", "http", "https", "tcp", "udp", "ip", "dns",
            "websocket", "웹소켓", "socket", "소켓", "rest", "restful", "api",
            "grpc", "graphql", "gateway", "게이트웨이", "packet", "패킷", "cdn", "proxy", "프록시"
        ]
    ),
    (
        "컴퓨터 사이언스", "#0d9488",  # Teal: 자료구조 / 알고리즘
        [
            "알고리즘", "algorithm", "자료구조", "data structure", "그리디", "greedy",
            "동적 계획법", "다이나믹 프로그래밍", "dynamic programming", "백트래킹",
            "backtracking", "분할 정복", "divide and conquer", "이진 탐색", "binary search",
            "bfs", "dfs", "다익스트라", "dijkstra", "최단 경로", "최소 신장 트리",
            "시간 복잡도", "빅오", "big-o", "재귀", "recursion", "메모이제이션",
            "memoization", "투 포인터", "슬라이딩 윈도우", "정렬 알고리즘", "해시 테이블"
        ]
    ),
    (
        "컴퓨터 사이언스", "#475569",  # Slate: 저수준 / OS / 메모리 / 임베디드
        [
            "memory", "메모리", "thread", "스레드", "process", "프로세스", "동시성",
            "concurrency", "async", "coroutine", "gc", "garbage collection", "커널",
            "kernel", "os", "운영체제", "c++", "rust", "c언어", "러스트", "컴파일러",
            "compiler", "assembly", "포인터", "pointer", "임베디드", "embedded",
            "펌웨어", "firmware", "mcu", "gpio", "아두이노", "arduino", "stm32"
        ]
    ),
    (
        "컴퓨터 사이언스", "#e11d48",  # Rose: 테스트 / 디버깅 / 트러블슈팅
        [
            "test", "테스트", "tdd", "mock", "debug", "디버그", "디버깅",
            "exception", "error", "에러", "예외", "logging", "로깅", "log", "로그",
            "monitoring", "모니터링", "sentry", "troubleshoot", "트러블슈팅", "장애"
        ]
    ),
]

# 일반 / 비개발 도메인 (2차 매칭)
GENERAL_DOMAIN_RULES = [
    (
        "자연과학", "#16a34a",  # Green: 자연 / 환경 / 생물 / 지구
        ["비", "날씨", "광합성", "생태", "식물", "지구", "기후", "바다", "환경", "생물", "동물", "숲", "나무"]
    ),
    (
        "자연과학", "#0284c7",  # Sky Blue: 물리 / 화학 / 우주
        ["우주", "원자", "양자", "물리", "화학", "상대성", "행성", "중력", "빛", "별", "은하", "과학", "블랙홀"]
    ),
    (
        "경제/금융", "#b45309",  # Warm Amber: 경제 / 금융 / 비즈니스
        ["인플레이션", "금리", "환율", "주식", "경제", "투자", "은행", "화폐", "돈", "부동산", "시장", "자본"]
    ),
    (
        "의학/생명", "#be123c",  # Crimson: 의학 / 인체 / 건강 / 생명공학
        ["면역", "뇌", "심장", "세포", "의학", "바이러스", "백신", "호르몬", "건강", "의료", "소화", "혈액", "수면", "생명공학", "유전자", "단백질"]
    ),
    (
        "인문/사회", "#8b5cf6",  # Purple: 인문 / 사회 / 예술 / 역사
        ["역사", "철학", "음악", "미술", "문학", "사회", "법률", "헌법", "정치", "문화", "예술"]
    ),
]

ALL_DOMAIN_RULES = DEV_DOMAIN_RULES + GENERAL_DOMAIN_RULES

FALLBACK_PALETTE = [
    "#2563eb",  # Blue
    "#059669",  # Emerald
    "#7c3aed",  # Violet
    "#d97706",  # Amber
    "#0891b2",  # Cyan
    "#4f46e5",  # Indigo
    "#e11d48",  # Rose
    "#475569",  # Slate
]


def match_domain(topic: str):
    """주제 키워드로 (대분류, 색상) 규칙을 찾는다. 매칭 실패 시 None."""
    t = topic.lower()
    for domain, color, keywords in ALL_DOMAIN_RULES:
        if any(kw in t for kw in keywords):
            return domain, color
    return None


def resolve_accent(topic: str, custom_accent: str | None) -> str:
    """악센트 색상을 결정한다: 사용자 지정값 -> 도메인 키워드 -> 해시 fallback"""
    if custom_accent:
        cleaned = custom_accent.strip()
        if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", cleaned):
            return cleaned.lower()

    matched = match_domain(topic)
    if matched:
        return matched[1]

    # 키워드가 없는 경우 결정론적 해시 분배
    idx = sum(ord(c) for c in topic) % len(FALLBACK_PALETTE)
    return FALLBACK_PALETTE[idx]


def resolve_category(topic: str) -> str:
    """주제의 상위 대분류를 반환한다 (docs-upload 카테고리 체계와 동일한 이름).
    매칭 실패 시 빈 문자열."""
    matched = match_domain(topic)
    return matched[0] if matched else ""


def category_colors() -> dict:
    """상위 대분류 -> 대표 악센트 색상 (해당 대분류의 첫 규칙 색상).

    docs 아카이브 서버의 카테고리별 색상은 이 표와 일치시킨다.
    한 대분류가 여러 색을 쓰는 경우(예: 컴퓨터 사이언스 = 알고리즘/저수준/테스트)
    카테고리 배지는 대표색 하나만 쓰고, 개별 문서의 내부 악센트는 주제에 따라 달라진다.
    `python3 build.py --categories` 로 출력한다."""
    out = {}
    for domain, color, _ in ALL_DOMAIN_RULES:
        out.setdefault(domain, color)
    return out


def main():
    if "--categories" in sys.argv:
        for name, color in category_colors().items():
            print(f"{color}\t{name}")
        return

    default_shell = pathlib.Path(__file__).resolve().parent.parent / "assets" / "shell.html"

    p = argparse.ArgumentParser()
    p.add_argument("--shell", default=str(default_shell), help="assets/shell.html 경로 (기본값: 스킬 assets/shell.html)")
    p.add_argument("--slug", help="문서 고유 영문 kebab-case 슬러그 (예: hexagonal-architecture). --out 미지정 시 /tmp/eli5-build/<slug>.html 로 출력")
    p.add_argument("--dir", help="중간 산출물(definition.html, diagram.svg, steps.js)이 위치한 디렉토리. 미지정 시 --slug 기반 /tmp/eli5-build/<slug> 우선 탐색")
    p.add_argument("--diagram", help="생성한 SVG 파일 경로 (미지정 시 --dir 또는 /tmp/eli5-build/<slug> 탐색)")
    p.add_argument("--steps", help="생성한 STEPS 배열(JS 리터럴) 파일 경로 (미지정 시 --dir 또는 /tmp/eli5-build/<slug> 탐색)")
    p.add_argument("--definition", help="한 눈 정의 블록(HTML 조각) 파일 경로 (미지정 시 --dir 또는 /tmp/eli5-build/<slug> 탐색)")
    p.add_argument("--topic", required=True)
    p.add_argument("--mode", required=True, choices=["개념 모드", "구현 모드"])
    p.add_argument("--accent", default=None, help="악센트 색상 hex (예: #059669). 미지정 시 주제 기반 자동 선택")
    p.add_argument("--out", default=None, help="최종 HTML 파일 경로 (미지정 시 /tmp/eli5-build/<slug>.html 로 자동 결정)")
    a = p.parse_args()

    # 1. 중간 산출물 디렉토리 탐색
    base_dir = None
    if a.dir:
        base_dir = pathlib.Path(a.dir)
    elif a.slug:
        candidate = pathlib.Path(f"/tmp/eli5-build/{a.slug}")
        if candidate.is_dir():
            base_dir = candidate

    # fallback: 만약 /tmp/eli5-build/<slug>가 없더라도 /tmp/eli5-build/ 에 중간 파일들이 있다면 사용
    if not base_dir and pathlib.Path("/tmp/eli5-build").is_dir():
        base_dir = pathlib.Path("/tmp/eli5-build")

    # 2. 다이어그램, 스텝, 정의 파일 경로 결정
    def resolve_input_file(cli_arg: str | None, filename: str) -> pathlib.Path:
        if cli_arg:
            return pathlib.Path(cli_arg)
        if base_dir and (base_dir / filename).is_file():
            return base_dir / filename
        sys.exit(f"오류: '{filename}' 파일을 찾을 수 없습니다. --{filename.split('.')[0]} 또는 --dir / --slug 인자를 확인해주세요.")

    diagram_path = resolve_input_file(a.diagram, "diagram.svg")
    steps_path = resolve_input_file(a.steps, "steps.js")
    definition_path = resolve_input_file(a.definition, "definition.html")

    # 3. 셸 파일 확인
    shell_path = pathlib.Path(a.shell)
    if not shell_path.is_file():
        sys.exit(f"오류: 셸 템플릿 파일을 찾을 수 없습니다: {shell_path}")

    # 4. 출력 파일 경로 결정
    if a.out:
        out_path = pathlib.Path(a.out)
    elif a.slug:
        out_path = pathlib.Path(f"/tmp/eli5-build/{a.slug}.html")
    else:
        sys.exit("오류: --out 또는 --slug 인자 중 최소 하나는 반드시 지정해야 합니다.")

    html = shell_path.read_text(encoding="utf-8")
    svg = diagram_path.read_text(encoding="utf-8").strip()
    steps = steps_path.read_text(encoding="utf-8").strip().rstrip(";")
    define = definition_path.read_text(encoding="utf-8").strip()

    if not steps.startswith("["):
        sys.exit("STEPS 파일은 '[' 로 시작하는 JS 배열 리터럴이어야 합니다.")
    if "<svg" not in svg:
        sys.exit("다이어그램 파일에 <svg> 요소가 없습니다.")
    if 'class="one"' not in define:
        sys.exit('정의 파일에 <p class="one"> 한 문장 정의가 없습니다.')

    accent_color = resolve_accent(a.topic, a.accent)
    category = resolve_category(a.topic)

    markers = (
        "<!--__DIAGRAM__-->",
        "<!--__DEFINITION__-->",
        "/*__STEPS__*/[]",
        "__TOPIC__",
        "__MODE__",
        "__ACCENT__",
    )
    for marker in markers:
        if marker not in html:
            sys.exit(f"셸 템플릿에서 마커를 찾지 못했습니다: {marker}")

    html = html.replace("<!--__DIAGRAM__-->", svg)
    html = html.replace("<!--__DEFINITION__-->", define)
    html = html.replace("/*__STEPS__*/[]", steps)
    html = html.replace("__TOPIC__", a.topic)
    html = html.replace("__MODE__", a.mode)
    html = html.replace("__ACCENT__", accent_color)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"생성 완료: {out_path}  ({len(html):,} bytes, accent: {accent_color})")
    if category:
        print(f"상위 대분류: {category}   (docs-upload 업로드 시 --category \"{category}\" 로 전달)")


if __name__ == "__main__":
    main()
