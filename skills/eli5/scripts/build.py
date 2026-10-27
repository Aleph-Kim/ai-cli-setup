#!/usr/bin/env python3
"""셸 템플릿에 주제 · SVG · STEPS 배열 · 악센트 색상을 주입해 최종 HTML을 만든다."""
import argparse, json, pathlib, re, sys

# ─────────────────────────────────────────────────────────────────────────────
# 도메인 분류표 (단일 출처)
#
# 각 항목: ("상위 대분류", "악센트 색상", [주제 키워드])
#   - "상위 대분류" 이름은 docs-upload 스킬의 카테고리 체계와 반드시 일치시킨다.
#     (skills/docs-upload/scripts/upload.py 가 이 표를 직접 불러와 사용)
#   - 색 구분을 위해 한 대분류가 여러 규칙으로 쪼개질 수 있다 (예: 컴퓨터 사이언스).
#   - 위에서부터 첫 매칭이 채택되므로, 좁은 주제를 먼저 둔다.
#   - 영문 키워드는 단어 단위, 한글 키워드는 조사가 붙으므로 부분 문자열로 매칭한다.
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
            "생성 모델", "생성형", "벡터 데이터베이스", "벡터 db",
            "ocr", "광학 문자", "컴퓨터 비전", "computer vision", "이미지 인식", "객체 인식"
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
            "container", "배포", "deploy", "serverless", "lambda", "infra", "인프라",
            "로드밸런서", "로드 밸런서", "load balancer", "로드밸런싱", "로드 밸런싱",
            "load balancing", "부하 분산", "서버 클러스터", "스케일 아웃", "scale out",
            "고가용성", "페일오버", "failover"
        ]
    ),
    (
        "소프트웨어 아키텍처", "#d97706",  # Amber: 시스템 설계 / 메시징 / 큐
        [
            "architecture", "아키텍처", "hexagonal", "헥사고날", "clean architecture",
            "클린", "ddd", "domain driven", "kafka", "카프카", "rabbitmq", "mq",
            "queue", "메시지 큐", "큐잉", "event", "이벤트", "msa", "microservice", "마이크로서비스",
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
            "grpc", "graphql", "gateway", "게이트웨이", "packet", "패킷", "cdn", "proxy", "프록시",
            "블루투스", "bluetooth", "와이파이", "wifi", "wi-fi", "무선", "wireless", "radio",
            "주파수", "frequency", "스펙트럼", "안테나", "지그비", "zigbee", "nfc", "lora",
            "lte", "5g", "셀룰러", "cellular", "호핑"
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
        ["강수", "빗방울", "비가 오", "날씨", "광합성", "생태", "식물", "지구", "기후", "바다", "환경", "생물", "동물", "삼림", "나무"]
    ),
    (
        "자연과학", "#0284c7",  # Sky Blue: 물리 / 화학 / 우주
        ["우주", "원자", "양자", "물리", "화학", "상대성", "행성", "중력", "빛의", "빛이", "항성", "별의", "은하", "과학", "블랙홀"]
    ),
    (
        "경제/금융", "#b45309",  # Warm Amber: 경제 / 금융 / 비즈니스
        ["인플레이션", "물가", "지수", "금리", "환율", "주식", "주가", "경제", "투자", "은행", "화폐", "돈의", "돈이", "통화", "부동산", "시장", "자본"]
    ),
    (
        "의학/생명", "#be123c",  # Crimson: 의학 / 인체 / 건강 / 생명공학
        ["면역", "두뇌", "뇌의", "뇌과학", "심장", "세포", "의학", "바이러스", "백신", "호르몬", "건강", "의료", "소화", "혈액", "수면", "생명공학", "유전자", "단백질"]
    ),
    (
        "인문/사회", "#8b5cf6",  # Purple: 인문 / 사회 / 예술 / 역사
        ["역사", "철학", "음악", "미술", "문학", "사회", "법률", "헌법", "정치", "문화", "예술"]
    ),
]

ALL_DOMAIN_RULES = DEV_DOMAIN_RULES + GENERAL_DOMAIN_RULES

# 부분 문자열 매칭에서 1글자 키워드는 와일드카드 (예: '비' → '컴퓨터 비전' 오분류)
_short = [kw for _, _, kws in ALL_DOMAIN_RULES for kw in kws if len(kw) < 2]
assert not _short, f"1글자 키워드 금지: {_short}"

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
    matched = match_all_domains(topic)
    return matched[0] if matched else None


def keyword_in(kw: str, t: str) -> bool:
    # 짧은 영문 약어가 다른 단어 안에서 잡히는 오탐 방지 (uuid 안의 ui, linux 안의 ux)
    if kw.isascii():
        return re.search(rf"(?<![a-z0-9]){re.escape(kw)}(?:s|es)?(?![a-z0-9])", t) is not None
    return kw in t


def match_all_domains(topic: str) -> list[tuple[str, str]]:
    """주제에 걸리는 모든 (대분류, 색상) 규칙을 선언 순서대로 반환"""
    t = topic.lower()
    return [(domain, color) for domain, color, keywords in ALL_DOMAIN_RULES if any(keyword_in(kw, t) for kw in keywords)]


def domain_of_color(color: str) -> str:
    """분류표 색상에 해당하는 대분류 (표에 없는 색이면 빈 문자열)"""
    for domain, c, _ in ALL_DOMAIN_RULES:
        if c == color:
            return domain
    return ""


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


def cap_tall_svg(svg_open: str, min_font: float | None = None) -> str:
    """세로로 긴 다이어그램(viewBox 높이/폭 0.35 이상)의 렌더링 높이를 420px 안팎으로 제한하는 max-width 주입
    (폭 100%로 늘어나 하단 단계 설명이 화면 밖으로 밀리는 문제 방지).
    단, 가장 작은 글자(min_font)가 화면에서 12px 미만이 될 만큼은 줄이지 않는다."""
    m = re.search(r'viewBox="([^"]*)"', svg_open)
    if not m:
        return svg_open
    _, _, w, h = (float(v) for v in re.split(r"[\s,]+", m.group(1).strip()))
    ratio = h / w
    if ratio < 0.35:
        return svg_open
    cap = 420 / ratio
    if min_font:
        cap = max(cap, w * 12 / min_font)
    return svg_open + f' style="max-width:{round(cap)}px;margin:0 auto"'


def _attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\s{name}="([^"]*)"', tag)
    return m.group(1) if m else None


def check_highlight(svg: str, steps: str) -> tuple[list[str], list[str]]:
    """단계별 하이라이트가 그림과 어긋나는지 검사해 (오류, 경고) 목록을 반환한다.
    - data-edge 는 data-from / data-to 로 연결 하나만 가리켜야 하고, 밝은 화살표의 양 끝 노드도 밝아야 한다
    - data-parent 가 있는 노드가 밝으면 그 부모(상자, 영역 라벨)도 밝아야 한다"""
    errors, warnings = [], []
    nodes = {}
    for tag in re.findall(r"<g\s[^>]*data-node=[^>]*>", svg):
        nodes[_attr(tag, "data-node")] = _attr(tag, "data-parent")
    edges = {}
    for tag, body in re.findall(r"(<g\s[^>]*data-edge=[^>]*>)(.*?)</g>", svg, flags=re.DOTALL):
        eid, src, dst = _attr(tag, "data-edge"), _attr(tag, "data-from"), _attr(tag, "data-to")
        edges[eid] = (src, dst)
        if not src or not dst:
            errors.append(f"화살표 {eid}: data-from / data-to 가 없음")
        for end in (src, dst):
            if end and end not in nodes:
                errors.append(f"화살표 {eid}: 끝 노드 {end} 가 SVG에 없음")
        if len(re.findall(r"<(?:path|line|polyline)\b", body)) > 1:
            errors.append(f"화살표 {eid}: 선이 2개 이상. 끝점마다 data-edge 를 나눌 것")
    for nid, parent in nodes.items():
        if parent and parent not in nodes:
            errors.append(f"노드 {nid}: data-parent {parent} 가 SVG에 없음")

    ids = lambda s: re.findall(r"['\"]([^'\"]+)['\"]", s)
    node_lists = [ids(s) for s in re.findall(r"\bnodes\s*:\s*\[([^\]]*)\]", steps)]
    edge_lists = [ids(s) for s in re.findall(r"\bedges\s*:\s*\[([^\]]*)\]", steps)]
    if len(node_lists) != len(edge_lists):
        errors.append("steps.js 의 nodes 와 edges 개수가 다름. 모든 단계에 둘 다 적을 것")
        return errors, warnings

    used = set()
    for i, (lit_nodes, lit_edges) in enumerate(zip(node_lists, edge_lists), 1):
        used |= set(lit_nodes) | set(lit_edges)
        for n in lit_nodes:
            if n not in nodes:
                errors.append(f"{i}단계: 노드 {n} 가 SVG에 없음")
        for e in lit_edges:
            if e not in edges:
                errors.append(f"{i}단계: 화살표 {e} 가 SVG에 없음")
        if not lit_nodes and not lit_edges:
            continue
        for e in lit_edges:
            dim = [end for end in edges.get(e, ()) if end and end in nodes and end not in lit_nodes]
            if dim:
                errors.append(f"{i}단계: 화살표 {e} 는 밝은데 끝 노드 {', '.join(dim)} 는 흐림")
        for n in lit_nodes:
            parent = nodes.get(n)
            if parent and parent not in lit_nodes:
                errors.append(f"{i}단계: 노드 {n} 는 밝은데 부모 {parent} 는 흐림")
        for parent in {p for p in nodes.values() if p} & set(lit_nodes):
            children = [c for c, p in nodes.items() if p == parent]
            if not set(children) & set(lit_nodes):
                warnings.append(f"{i}단계: {parent} 는 밝은데 안의 노드 {', '.join(children)} 가 모두 흐림")
    unused = (set(nodes) | set(edges)) - used
    if unused:
        warnings.append(f"어느 단계에서도 밝아지지 않는 요소: {', '.join(sorted(unused))}")
    return errors, warnings


def tag_color_pairs(raw: str) -> str:
    """tag-colors.json({"키워드": "#hex"})을 셸 TAG_COLOR 배열 리터럴로 변환 (키워드는 소문자, 선언 순서 유지)"""
    colors = json.loads(raw)
    bad = [k for k, v in colors.items() if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", str(v))]
    if bad:
        sys.exit(f"tag-colors.json 색상값이 hex 형식이 아닙니다: {bad}")
    return json.dumps([[k.lower(), v] for k, v in colors.items()], ensure_ascii=False)


CODE_LINE_LIMIT = {"개념 모드": 10, "구현 모드": 15}
TERM_LIMIT = 3
MIXED_STEP_LIMIT = 11
MODE_BADGE = {"혼합 모드": "개념 + 구현"}

STR_RE = re.compile(r"`(?:\\.|[^`\\])*`|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\"")
# 대문자 약어(DER), camelCase(retainUntilConsumed), 숫자 섞인 식별자(x5c, UInt64), 점이나 밑줄 포함 이름(app.js)
TERM_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:[A-Z]{2,}[A-Za-z0-9]*|[a-z]+[A-Z][A-Za-z0-9]*|[A-Za-z]+[0-9][A-Za-z0-9]*|[A-Za-z0-9]+[._][A-Za-z0-9._]+)(?![A-Za-z0-9])"
)


def split_steps(js: str) -> list[str]:
    """STEPS 배열 리터럴을 최상위 객체 소스 단위로 나눈다 (문자열 안의 괄호는 무시)"""
    objs, depth, start, i = [], 0, 0, 0
    while i < len(js):
        c = js[i]
        if c in "`'\"":
            m = STR_RE.match(js, i)
            i = m.end() if m else i + 1
            continue
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                objs.append(js[start:i + 1])
        i += 1
    return objs


def step_field(obj: str, name: str) -> str:
    m = re.search(rf"\b{name}\s*:\s*({STR_RE.pattern})", obj)
    return m.group(1)[1:-1] if m else ""


def check_steps(steps: str, mode: str, topic: str = "") -> list[str]:
    """단계별 코드 줄 수, 설명문 영문 용어 수 점검 경고"""
    warnings = []
    # 주제어 자체와 버전 번호는 독자가 이미 아는 말이라 용어 수에서 제외
    topic_words = set(re.findall(r"[a-z0-9]+", topic.lower()))
    objs = split_steps(steps)
    first_phase = step_field(objs[0], "phase") if objs else ""
    if mode == "혼합 모드" and len(objs) > MIXED_STEP_LIMIT:
        warnings.append(f"혼합 모드 단계 {len(objs)}개 (상한 {MIXED_STEP_LIMIT}개)")
    for n, obj in enumerate(objs, 1):
        # 혼합 모드는 첫 phase만 개념 모드 기준, 나머지는 구현 모드 기준
        step_mode = mode
        if mode == "혼합 모드":
            step_mode = "개념 모드" if step_field(obj, "phase") == first_phase else "구현 모드"
        limit = CODE_LINE_LIMIT.get(step_mode)
        code = step_field(obj, "code").strip("\n")
        lines = code.count("\n") + 1 if code else 0
        if limit and lines > limit:
            warnings.append(f"{n}단계 코드 {lines}줄 ({step_mode} 상한 {limit}줄)")
        terms = [
            w for w in dict.fromkeys(TERM_RE.findall(step_field(obj, "summary")))
            if w.lower() not in topic_words and not w[0].isdigit()
        ]
        if len(terms) > TERM_LIMIT:
            warnings.append(f"{n}단계 설명에 영문 용어 {len(terms)}개 ({', '.join(terms)})")
    return warnings


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
    p.add_argument("--links", help="참고 링크 블록(HTML 조각) 파일 경로 (미지정 시 --dir 또는 /tmp/eli5-build/<slug> 탐색)")
    p.add_argument("--tag-colors", help="where 배지 상징색 JSON 파일 경로 (미지정 시 --dir 또는 /tmp/eli5-build/<slug> 탐색)")
    p.add_argument("--topic", required=True)
    p.add_argument("--mode", required=True, choices=["개념 모드", "구현 모드", "혼합 모드"])
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

    # links.html 은 선택 사항 — 검증된 링크가 하나도 없으면 아예 두지 않고, 그 경우 참고 링크 섹션도 통째로 빠진다.
    links_path = None
    if a.links:
        links_path = pathlib.Path(a.links)
    elif base_dir and (base_dir / "links.html").is_file():
        links_path = base_dir / "links.html"

    # tag-colors.json 도 선택 사항 — 없으면 where 배지가 모두 강조색으로 나온다.
    tag_colors_path = None
    if a.tag_colors:
        tag_colors_path = pathlib.Path(a.tag_colors)
    elif base_dir and (base_dir / "tag-colors.json").is_file():
        tag_colors_path = base_dir / "tag-colors.json"

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
    links = links_path.read_text(encoding="utf-8").strip() if links_path else ""
    tag_colors = tag_color_pairs(tag_colors_path.read_text(encoding="utf-8")) if tag_colors_path else "[]"

    if not steps.startswith("["):
        sys.exit("STEPS 파일은 '[' 로 시작하는 JS 배열 리터럴이어야 합니다.")
    if "<svg" not in svg:
        sys.exit("다이어그램 파일에 <svg> 요소가 없습니다.")
    # 셸이 width:100%;height:auto 로 크기를 잡으므로 루트 svg 의 고정 크기 속성 제거
    svg_open, gt, svg_rest = svg.partition(">")
    svg_open = re.sub(r'\s+(?:width|height)="[^"]*"', "", svg_open)
    font_sizes = [float(v) for v in re.findall(r'font-size="([\d.]+)"', svg_rest)]
    svg_open = cap_tall_svg(svg_open, min(font_sizes, default=None))
    svg = svg_open + gt + svg_rest
    if "viewBox" not in svg_open:
        print("경고: 루트 <svg> 에 viewBox 가 없어 반응형 크기 조절이 되지 않습니다.")
    highlight_errors, highlight_warnings = check_highlight(svg, steps)
    if highlight_errors:
        sys.exit("다이어그램 하이라이트 오류:\n" + "\n".join(f"  - {e}" for e in highlight_errors))
    if 'class="one"' not in define:
        sys.exit('정의 파일에 <p class="one"> 한 문장 정의가 없습니다.')
    if links and 'class="refs-list"' not in links:
        sys.exit('참고 링크 파일이 비어 있지 않은데 <ul class="refs-list"> 가 없습니다. 검증된 링크가 없으면 links.html 을 만들지 마세요.')

    accent_color = resolve_accent(a.topic, a.accent)
    category = resolve_category(a.topic)
    notices = list(highlight_warnings)
    if not tag_colors_path:
        notices.append("tag-colors.json 없음 — where 배지가 모두 강조색으로 나옴. 기술 이름 배지가 있으면 상징색을 조사해 작성")

    # 다의어 키워드 경합 (예: '인덱스' → 데이터베이스 vs 경제/금융) 노출
    competing = [d for d, _ in match_all_domains(a.topic) if d != category]
    if competing:
        notices.append(f"다른 대분류에도 매칭됨: {', '.join(dict.fromkeys(competing))} — 오분류면 --accent/--category 수동 교정")

    # --accent 수동 지정 시 대분류도 함께 따라가도록 동기화 (색과 카테고리 불일치 방지)
    if a.accent:
        accent_domain = domain_of_color(accent_color)
        if accent_domain and accent_domain != category:
            notices.append(f"악센트 색 기준 대분류 '{accent_domain}'로 변경 (주제 키워드 매칭: '{category or '없음'}')")
            category = accent_domain
        elif not accent_domain:
            notices.append("지정한 악센트 색은 분류표에 없어 대분류는 주제 키워드 매칭 결과 유지")

    markers = (
        "<!--__DIAGRAM__-->",
        "<!--__DEFINITION__-->",
        "<!--__LINKS__-->",
        "/*__STEPS__*/[]",
        "/*__TAG_COLOR__*/[]",
        "__TOPIC__",
        "__MODE__",
        "__ACCENT__",
    )
    for marker in markers:
        if marker not in html:
            sys.exit(f"셸 템플릿에서 마커를 찾지 못했습니다: {marker}")

    html = html.replace("<!--__DIAGRAM__-->", svg)
    html = html.replace("<!--__DEFINITION__-->", define)
    if links:
        html = html.replace("<!--__LINKS__-->", links)
    else:
        # 검증된 링크가 없으면 참고 링크 섹션을 통째로 제거한다.
        html = re.sub(r'\s*<section class="refs">.*?</section>', "", html, flags=re.DOTALL)
    html = html.replace("/*__STEPS__*/[]", steps)
    html = html.replace("/*__TAG_COLOR__*/[]", tag_colors)
    html = html.replace("__TOPIC__", a.topic)
    html = html.replace("__MODE__", MODE_BADGE.get(a.mode, a.mode))
    html = html.replace("__ACCENT__", accent_color)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"생성 완료: {out_path}  ({len(html):,} bytes, accent: {accent_color})")
    for w in check_steps(steps, a.mode, a.topic):
        print(f"경고: {w}")
    for n in notices:
        print(f"주의: {n}")
    if category:
        print(f"상위 대분류: {category}   (docs-upload 업로드 시 --category \"{category}\" 로 전달)")
    else:
        print("상위 대분류: 없음 — 주제 키워드가 분류표에 없음. docs-upload 업로드 시 --category 수동 지정 필요")


if __name__ == "__main__":
    main()
