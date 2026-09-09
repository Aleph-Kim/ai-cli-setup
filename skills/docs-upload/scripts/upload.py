#!/usr/bin/env python3
"""Docs 아카이브 서버에 카테고리를 조회/선택/생성 후 HTML 문서를 업로드하는 스크립트."""

import argparse
import html
import json
import mimetypes
import os
import pathlib
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid


def load_env_file(filepath: pathlib.Path) -> dict:
    """간단한 .env 파일 파서."""
    env_vars = {}
    if not filepath.is_file():
        return env_vars

    for line in filepath.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, val = line.split("=", 1)
            env_vars[key.strip()] = val.strip().strip("'\"")
    return env_vars


import http.cookiejar
import ssl

cookie_jar = http.cookiejar.CookieJar()
try:
    ssl_context = ssl.create_default_context()
    if not ssl_context.get_ca_certs() and not (ssl.get_default_verify_paths().openssl_cafile and os.path.exists(ssl.get_default_verify_paths().openssl_cafile)):
        ssl_context = ssl._create_unverified_context()
except Exception:
    ssl_context = ssl._create_unverified_context()

https_handler = urllib.request.HTTPSHandler(context=ssl_context)
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar), https_handler)


def get_xsrf_token() -> str:
    """쿠키에서 XSRF-TOKEN 추출."""
    for cookie in cookie_jar:
        if cookie.name == "XSRF-TOKEN":
            return urllib.parse.unquote(cookie.value)
    return ""


def api_request(url: str, method: str, api_key: str, data: bytes = None, headers: dict = None) -> dict:
    """API 요청 헬퍼."""
    req_headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": "docs-upload-skill/1.0",
    }
    xsrf = get_xsrf_token()
    if xsrf:
        req_headers["X-XSRF-TOKEN"] = xsrf

    if headers:
        req_headers.update(headers)

    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

    try:
        with opener.open(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        try:
            err_json = json.loads(error_body)
            msg = err_json.get("message") or err_json.get("error") or str(err_json)
        except Exception:
            msg = error_body
        sys.exit(f"API 요청 실패 [{method} {url}] (HTTP {e.code}): {msg}")
    except urllib.error.URLError as e:
        sys.exit(f"서버 접속 실패 ({url}): {e.reason}\n서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        sys.exit(f"요청 중 예외 발생: {e}")


def build_multipart_body(fields: dict, files: dict, boundary: str) -> bytes:
    """multipart/form-data 바이트 본문 생성."""
    lines = []

    for name, value in fields.items():
        if value is None:
            continue
        lines.append(f"--{boundary}".encode("utf-8"))
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode("utf-8"))
        lines.append(b"")
        lines.append(str(value).encode("utf-8"))

    for name, (filename, content, mime) in files.items():
        lines.append(f"--{boundary}".encode("utf-8"))
        lines.append(
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"'.encode("utf-8")
        )
        lines.append(f"Content-Type: {mime}".encode("utf-8"))
        lines.append(b"")
        lines.append(content)

    lines.append(f"--{boundary}--".encode("utf-8"))
    lines.append(b"")

    return b"\r\n".join(lines)


def fetch_categories(base_url: str, api_key: str) -> list:
    """서버에서 등록된 카테고리 목록 조회."""
    res = api_request(f"{base_url}/admin/categories", "GET", api_key)
    return res.get("data", [])


def create_category(base_url: str, api_key: str, name: str) -> dict:
    """새 카테고리 생성."""
    payload = json.dumps({"name": name}).encode("utf-8")
    res = api_request(
        f"{base_url}/admin/categories",
        "POST",
        api_key,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    category = res.get("data", {})
    print(f"  [새 카테고리 생성] {category.get('name')} (id: {category.get('id')})")
    return category


# 도메인별 표준 상위 카테고리 매핑 규칙
#
# 대분류 이름과 키워드는 eli5 스킬의 분류표와 일치시킨다 (수동 동기화).
#   원본: skills/eli5/scripts/build.py 의 DEV_DOMAIN_RULES / GENERAL_DOMAIN_RULES
# eli5 는 색상 구분을 위해 "컴퓨터 사이언스" 등을 여러 규칙으로 쪼개지만,
# 카테고리 관점에서는 하나이므로 여기서는 키워드를 대분류별로 합쳐 둔다.
# 단, 이 스킬은 주제 + HTML 본문 앞부분까지 매칭하므로, 본문 상용어와 충돌하는
# 지나치게 일반적인 단일 단어(test, error, log 등)는 제외한다.
DOMAIN_TAXONOMY = {
    "보안": [
        "oauth", "jwt", "ssl", "tls", "토큰", "보안", "인증", "인가", "암호화",
        "세션", "쿠키", "rbac", "cors", "csrf", "xss", "crypto", "비밀번호"
    ],
    "인공지능/머신러닝": [
        "인공지능", "머신러닝", "machine learning", "딥러닝", "deep learning",
        "신경망", "neural", "llm", "gpt", "트랜스포머", "transformer", "임베딩",
        "embedding", "파인튜닝", "프롬프트", "prompt", "rag", "확산 모델", "diffusion",
        "강화학습", "생성형", "생성 모델", "벡터 데이터베이스"
    ],
    "데이터베이스": [
        "database", "db", "sql", "nosql", "mysql", "postgresql", "sqlite",
        "redis", "mongodb", "인덱스", "트랜잭션", "orm", "erd", "정규화", "샤딩", "캐시"
    ],
    "인프라/DevOps": [
        "docker", "도커", "container", "컨테이너", "kubernetes", "k8s", "ci/cd",
        "jenkins", "github actions", "linux", "리눅스", "배포", "인프라", "devops",
        "클라우드", "aws", "gcp", "azure", "terraform", "serverless", "nginx"
    ],
    "소프트웨어 아키텍처": [
        "architecture", "아키텍처", "헥사고날", "hexagonal", "클린 아키텍처", "ddd",
        "도메인 주도", "디자인 패턴", "design pattern", "mvc", "msa", "마이크로서비스",
        "api 설계", "모듈", "kafka", "카프카", "메시지 큐", "pub/sub", "saga", "cqrs", "이벤트 기반"
    ],
    "웹/프론트엔드": [
        "css", "html", "dom", "javascript", "typescript", "react", "vue", "svelte",
        "next.js", "frontend", "프론트엔드", "브라우저", "렌더링", "ui", "ux",
        "웹 표준", "스타일", "상태관리", "redux", "tailwind", "webpack", "vite"
    ],
    "네트워크/통신": [
        "websocket", "웹소켓", "http", "https", "tcp", "udp", "ip", "dns", "socket",
        "소켓", "네트워크", "network", "push", "웹푸시", "rest", "restful", "grpc",
        "graphql", "gateway", "게이트웨이", "패킷", "cdn", "proxy", "프록시"
    ],
    "컴퓨터 사이언스": [
        "자료구조", "data structure", "알고리즘", "algorithm", "그리디", "greedy",
        "동적 계획법", "다이나믹 프로그래밍", "dynamic programming", "백트래킹",
        "분할 정복", "이진 탐색", "binary search", "bfs", "dfs", "다익스트라",
        "최단 경로", "최소 신장 트리", "시간 복잡도", "빅오", "재귀", "recursion",
        "메모이제이션", "정렬 알고리즘", "해시 테이블",
        "os", "운영체제", "프로세스", "스레드", "thread", "메모리", "동시성",
        "concurrency", "코루틴", "커널", "kernel", "컴파일러", "compiler", "포인터",
        "임베디드", "embedded", "펌웨어", "아두이노", "arduino",
        "테스트 코드", "단위 테스트", "tdd", "디버깅", "트러블슈팅", "스택 트레이스"
    ],
    "자연과학": [
        "광합성", "생태", "지구", "기후", "날씨", "환경", "생물", "동물", "식물",
        "우주", "원자", "양자", "물리", "화학", "상대성", "행성", "중력", "은하", "블랙홀"
    ],
    "의학/생명": [
        "면역", "심장", "세포", "의학", "바이러스", "백신", "호르몬", "건강",
        "의료", "소화", "혈액", "수면", "생명공학", "유전자", "단백질", "뇌과학"
    ],
    "경제/금융": [
        "인플레이션", "금리", "환율", "주식", "경제", "투자", "은행", "화폐",
        "부동산", "자본", "금융"
    ],
    "인문/사회": [
        "역사", "철학", "음악", "미술", "문학", "사회", "법률", "헌법", "정치", "문화", "예술"
    ]
}


def infer_domain_category(text: str) -> str:
    """텍스트(제목 및 내용)의 키워드를 분석하여 상위 도메인 카테고리를 추론."""
    lower_text = text.lower()
    for domain, keywords in DOMAIN_TAXONOMY.items():
        for kw in keywords:
            # 단어 단위 또는 부분 문자열 매칭
            if kw in lower_text:
                return domain
    return ""


def resolve_category(base_url: str, api_key: str, user_cat: str, html_text: str, topic: str) -> dict:
    """기존 카테고리 목록 중 적합한 상위 카테고리 탐색 -> 일치하는 것이 없으면 상위 도메인 카테고리 자동 생성."""
    categories = fetch_categories(base_url, api_key)

    # 1. 사용자가 명시적으로 카테고리를 지정한 경우
    if user_cat:
        for cat in categories:
            if str(cat.get("id")) == str(user_cat):
                return cat
            if str(cat.get("slug", "")).lower() == str(user_cat).lower():
                return cat
            if str(cat.get("name", "")).lower() == str(user_cat).lower():
                return cat
            # 슬래시/공백 무시 유연한 매칭 (예: "웹/프론트엔드" vs "웹 / 프론트엔드" vs "웹/프론트")
            norm_cat = re.sub(r"[\s/]", "", cat.get("name", "").lower())
            norm_user = re.sub(r"[\s/]", "", str(user_cat).lower())
            if norm_cat and norm_user and (norm_cat == norm_user or norm_cat in norm_user or norm_user in norm_cat):
                return cat

        return create_category(base_url, api_key, user_cat)

    # 2. 지정되지 않은 경우: 무관한 테스트 카테고리 제외
    excluded_names = {"test", "테스트", "기타", "temp", "임시"}
    valid_categories = [
        cat for cat in categories
        if cat.get("name", "").strip().lower() not in excluded_names
        and cat.get("slug", "").strip().lower() not in excluded_names
    ]

    combined_info = f"{topic} {html_text[:1000]}"
    inferred_domain = infer_domain_category(combined_info)

    # 2-1. 도메인 대분류가 추론된 경우: 해당 상위 카테고리 우선 매칭 또는 신규 생성
    if inferred_domain:
        norm_inferred = re.sub(r"[\s/]", "", inferred_domain.lower())
        for cat in valid_categories:
            norm_cat = re.sub(r"[\s/]", "", cat.get("name", "").lower())
            if norm_cat and (norm_cat == norm_inferred or norm_inferred in norm_cat or norm_cat in norm_inferred):
                return cat
        # 기존에 상위 카테고리가 없으면 대분류로 새로 생성
        return create_category(base_url, api_key, inferred_domain)

    # 2-2. 도메인 추론이 안 된 경우: 기존 유효 카테고리 매칭 탐색
    clean_topic = re.sub(r"[^\w\s가-힣]", " ", topic).strip().lower()
    topic_tokens = set(clean_topic.split())

    for cat in valid_categories:
        cat_name = cat.get("name", "").strip().lower()
        cat_slug = cat.get("slug", "").strip().lower()

        if not cat_name and not cat_slug:
            continue

        if cat_name == clean_topic or (cat_slug and cat_slug == clean_topic):
            return cat
        if cat_name in topic_tokens or (cat_slug and cat_slug in topic_tokens):
            return cat
        if len(cat_name) >= 2 and cat_name in clean_topic:
            return cat

    # 2-3. 최종 fallback: 정제된 주제로 새 카테고리 생성
    derived_name = re.sub(r"\(.*?\)", "", topic).strip()
    derived_name = re.sub(r"[\[\]{}<>]", "", derived_name).strip()
    target_category_name = derived_name.split()[0] if derived_name else "기술 일반"

    return create_category(base_url, api_key, target_category_name)


def extract_topic_from_html(content: str) -> str:
    """HTML에서 제목 추출."""
    m = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
    if m:
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if t:
            return t
    m = re.search(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
    if m:
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if t:
            return t
    return ""


def extract_description_from_html(content: str) -> str:
    """HTML에서 한 줄 정의/설명 추출 (eli5 <p class="one">)."""
    m = re.search(r'<p[^>]*class=["\'][^"\']*one[^"\']*["\'][^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
    if m:
        t = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
        if t:
            return t
    return ""


def main():
    parser = argparse.ArgumentParser(description="Docs 서버에 카테고리를 조회/생성 후 HTML 문서를 업로드합니다.")
    parser.add_argument("--file", "-f", required=True, help="업로드할 HTML 파일 경로")
    parser.add_argument("--title", "-t", help="문서 제목 (생략 시 HTML에서 자동 추출)")
    parser.add_argument("--description", "-d", help="문서 설명 (생략 시 HTML에서 자동 추출)")
    parser.add_argument("--category", "-c", help="카테고리명/slug (생략 시 내용 기반 자동 매칭 또는 생성)")
    parser.add_argument("--slug", "-s", help="URL 슬러그 (생략 시 제목 기반 자동 생성)")
    parser.add_argument("--url", help="Docs 서버 베이스 URL (기본: .env의 DOCS_URL 또는 http://localhost:8000)")
    parser.add_argument("--key", "--password", "-k", help="API 키 또는 관리자 비밀번호 (기본: .env의 DOCS_PASSWORD)")
    parser.add_argument("--env-file", help="참조할 .env 파일 경로")
    args = parser.parse_args()

    # 1. 파일 검증
    target_file = pathlib.Path(args.file).resolve()
    if not target_file.is_file():
        sys.exit(f"오류: 업로드할 파일을 찾을 수 없습니다: {target_file}")

    file_content = target_file.read_text(encoding="utf-8", errors="replace")

    # 2. .env 파일 탐색 및 로드
    skill_root = pathlib.Path(__file__).resolve().parent.parent
    env_path = pathlib.Path(args.env_file).resolve() if args.env_file else (skill_root / ".env")
    env_vars = load_env_file(env_path)

    base_url = (
        args.url
        or env_vars.get("DOCS_URL")
        or os.environ.get("DOCS_URL")
        or "http://localhost:8000"
    ).rstrip("/")

    api_key = (
        args.key
        or env_vars.get("DOCS_PASSWORD")
        or env_vars.get("DOCS_API_KEY")
        or os.environ.get("DOCS_PASSWORD")
        or os.environ.get("DOCS_API_KEY")
        or ""
    )

    if not api_key:
        sys.exit(
            f"오류: 인증 비밀번호가 설정되지 않았습니다.\n"
            f"'{env_path}' 파일에 DOCS_PASSWORD=비밀번호 를 설정하거나 --key 인자를 전달해주세요."
        )

    # 3. 카테고리 조회 및 어울리는 카테고리 매칭/생성
    topic = args.title or extract_topic_from_html(file_content) or target_file.stem
    desc = args.description or extract_description_from_html(file_content) or None
    category = resolve_category(base_url, api_key, args.category, file_content, topic)

    # 4. 문서 업로드 요청
    boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
    file_bytes = target_file.read_bytes()
    mime_type = mimetypes.guess_type(target_file.name)[0] or "text/html"

    upload_slug = args.slug
    if not upload_slug and target_file.stem.lower() not in ("out", "index"):
        upload_slug = target_file.stem

    fields = {
        "title": topic,
        "description": desc,
        "category_id": category.get("id"),
        "slug": upload_slug,
    }

    files = {
        "html_file": (target_file.name, file_bytes, mime_type),
    }

    body = build_multipart_body(fields, files, boundary)
    endpoint = f"{base_url}/admin/visuals"

    res_data = api_request(
        endpoint,
        "POST",
        api_key,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )

    # 5. 결과 출력
    data = res_data.get("data", {})
    title = data.get("title", topic)
    slug = data.get("slug", "")
    page_url = data.get("url", f"{base_url}/visuals/{slug}")
    render_url = data.get("render_url", f"{base_url}/visuals/{slug}/render")
    cat_name = data.get("category", {}).get("name", category.get("name", "인터랙티브"))

    print("문서 업로드 완료!")
    print(f"- 제목: {title}")
    print(f"- 카테고리: {cat_name}")
    print(f"- 상세 페이지: {page_url}")
    print(f"- 렌더링 주소: {render_url}")


if __name__ == "__main__":
    main()
