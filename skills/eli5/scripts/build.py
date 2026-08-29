#!/usr/bin/env python3
"""셸 템플릿에 주제 · SVG · STEPS 배열 · 악센트 색상을 주입해 최종 HTML을 만든다."""
import argparse, pathlib, re, sys

# 개발/엔지니어링 특화 도메인 (1차 우선 매칭)
DEV_COLOR_RULES = [
    (
        "#4f46e5",  # Indigo: 보안 / 인증 / 인가 / 암호화 / 토큰
        [
            "auth", "oauth", "jwt", "ssl", "tls", "token", "보안", "인증", "인가",
            "암호화", "세션", "session", "쿠키", "cookie", "rbac", "cors", "csrf",
            "xss", "crypto", "secret", "비밀번호", "password", "oauth2"
        ]
    ),
    (
        "#059669",  # Emerald: 데이터베이스 / 캐시 / 저장소 / 쿼리
        [
            "db", "database", "sql", "rdbms", "nosql", "redis", "cache", "캐시",
            "postgres", "postgresql", "mysql", "mongodb", "sqlite", "인덱스", "index",
            "트랜잭션", "transaction", "orm", "jpa", "prisma", "migration", "sharding",
            "replication", "스토리지", "storage"
        ]
    ),
    (
        "#0891b2",  # Cyan: 클라우드 / DevOps / 인프라 / 컨테이너
        [
            "docker", "k8s", "kubernetes", "도커", "쿠버네티스", "aws", "gcp", "azure",
            "cloud", "클라우드", "terraform", "ci/cd", "cicd", "nginx", "컨테이너",
            "container", "배포", "deploy", "serverless", "lambda", "infra", "인프라"
        ]
    ),
    (
        "#d97706",  # Amber: 아키텍처 / 시스템 설계 / 메시징 / 큐
        [
            "architecture", "아키텍처", "hexagonal", "헥사고날", "clean architecture",
            "클린", "ddd", "domain driven", "kafka", "카프카", "rabbitmq", "mq",
            "queue", "큐", "event", "이벤트", "msa", "microservice", "마이크로서비스",
            "pattern", "패턴", "pub/sub", "pubsub", "saga", "cqrs"
        ]
    ),
    (
        "#7c3aed",  # Violet: 프론트엔드 / 웹 / UI / 렌더링
        [
            "react", "vue", "next.js", "nextjs", "svelte", "dom", "css", "html",
            "frontend", "프론트", "프론트엔드", "브라우저", "browser", "rendering",
            "렌더링", "ui", "ux", "상태관리", "redux", "zustand", "tailwind", "webpack", "vite"
        ]
    ),
    (
        "#475569",  # Slate: 저수준 / OS / 시스템 프로그래밍 / 메모리 / 임베디드
        [
            "memory", "메모리", "thread", "스레드", "process", "프로세스", "동시성",
            "concurrency", "async", "coroutine", "gc", "garbage collection", "커널",
            "kernel", "os", "운영체제", "c++", "rust", "c언어", "러스트", "컴파일러",
            "compiler", "assembly", "포인터", "pointer", "임베디드", "embedded",
            "펌웨어", "firmware", "mcu", "gpio", "아두이노", "arduino", "stm32"
        ]
    ),
    (
        "#e11d48",  # Rose: 테스트 / 디버깅 / 트러블슈팅 / 로깅 / 에러
        [
            "test", "테스트", "tdd", "mock", "debug", "디버그", "디버깅",
            "exception", "error", "에러", "예외", "logging", "로깅", "log", "로그",
            "monitoring", "모니터링", "sentry", "troubleshoot", "트러블슈팅", "장애"
        ]
    ),
    (
        "#2563eb",  # Blue: 네트워크 / 통신 / 프로토콜 / API
        [
            "network", "네트워크", "http", "https", "tcp", "udp", "ip", "dns",
            "websocket", "웹소켓", "socket", "소켓", "rest", "restful", "api",
            "grpc", "graphql", "gateway", "게이트웨이", "packet", "패킷", "cdn", "proxy", "프록시"
        ]
    ),
]

# 일반 / 비개발 보조 도메인 (2차 매칭)
GENERAL_COLOR_RULES = [
    (
        "#16a34a",  # Green: 자연 / 환경 / 생물 / 지구
        ["비", "날씨", "광합성", "생태", "식물", "지구", "기후", "바다", "환경", "생물", "동물", "숲", "나무"]
    ),
    (
        "#0284c7",  # Sky Blue: 물리 / 화학 / 과학 / 우주
        ["우주", "원자", "양자", "물리", "화학", "상대성", "행성", "중력", "빛", "별", "은하", "과학", "블랙홀"]
    ),
    (
        "#b45309",  # Warm Amber: 경제 / 금융 / 비즈니스
        ["인플레이션", "금리", "환율", "주식", "경제", "투자", "은행", "화폐", "돈", "부동산", "시장", "자본"]
    ),
    (
        "#be123c",  # Crimson: 의학 / 인체 / 건강 / 생리학
        ["면역", "뇌", "심장", "세포", "의학", "바이러스", "백신", "호르몬", "건강", "의료", "소화", "혈액", "수면"]
    ),
    (
        "#8b5cf6",  # Purple: 인문 / 사회 / 예술 / 역사
        ["역사", "철학", "음악", "미술", "문학", "사회", "법률", "헌법", "정치", "문화", "예술"]
    ),
]

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


def resolve_accent(topic: str, custom_accent: str | None) -> str:
    """악센트 색상을 결정한다: 사용자 지정값 -> 개발 도메인 키워드 -> 일반 도메인 키워드 -> 해시 fallback"""
    if custom_accent:
        cleaned = custom_accent.strip()
        if re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", cleaned):
            return cleaned.lower()

    t = topic.lower()
    for color, keywords in DEV_COLOR_RULES:
        if any(kw in t for kw in keywords):
            return color

    for color, keywords in GENERAL_COLOR_RULES:
        if any(kw in t for kw in keywords):
            return color

    # 키워드가 없는 경우 결정론적 해시 분배
    idx = sum(ord(c) for c in topic) % len(FALLBACK_PALETTE)
    return FALLBACK_PALETTE[idx]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--shell", required=True, help="assets/shell.html 경로")
    p.add_argument("--diagram", required=True, help="생성한 SVG 파일 경로")
    p.add_argument("--steps", required=True, help="생성한 STEPS 배열(JS 리터럴) 파일 경로")
    p.add_argument("--definition", required=True, help="한 눈 정의 블록(HTML 조각) 파일 경로")
    p.add_argument("--topic", required=True)
    p.add_argument("--mode", required=True, choices=["개념 모드", "구현 모드"])
    p.add_argument("--accent", default=None, help="악센트 색상 hex (예: #059669). 미지정 시 주제 기반 자동 선택")
    p.add_argument("--out", required=True)
    a = p.parse_args()

    html = pathlib.Path(a.shell).read_text(encoding="utf-8")
    svg = pathlib.Path(a.diagram).read_text(encoding="utf-8").strip()
    steps = pathlib.Path(a.steps).read_text(encoding="utf-8").strip().rstrip(";")
    define = pathlib.Path(a.definition).read_text(encoding="utf-8").strip()

    if not steps.startswith("["):
        sys.exit("STEPS 파일은 '[' 로 시작하는 JS 배열 리터럴이어야 합니다.")
    if "<svg" not in svg:
        sys.exit("다이어그램 파일에 <svg> 요소가 없습니다.")
    if 'class="one"' not in define:
        sys.exit('정의 파일에 <p class="one"> 한 문장 정의가 없습니다.')

    accent_color = resolve_accent(a.topic, a.accent)

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

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"생성 완료: {out}  ({len(html):,} bytes, accent: {accent_color})")


if __name__ == "__main__":
    main()
