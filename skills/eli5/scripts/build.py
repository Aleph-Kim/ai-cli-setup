#!/usr/bin/env python3
"""셸 템플릿에 주제 · SVG · STEPS 배열을 주입해 최종 HTML을 만든다."""
import argparse, pathlib, sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--shell", required=True, help="assets/shell.html 경로")
    p.add_argument("--diagram", required=True, help="생성한 SVG 파일 경로")
    p.add_argument("--steps", required=True, help="생성한 STEPS 배열(JS 리터럴) 파일 경로")
    p.add_argument("--definition", required=True, help="한 눈 정의 블록(HTML 조각) 파일 경로")
    p.add_argument("--topic", required=True)
    p.add_argument("--mode", required=True, choices=["개념 모드", "구현 모드"])
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

    for marker in ("<!--__DIAGRAM__-->", "<!--__DEFINITION__-->", "/*__STEPS__*/[]", "__TOPIC__", "__MODE__"):
        if marker not in html:
            sys.exit(f"셸 템플릿에서 마커를 찾지 못했습니다: {marker}")

    html = html.replace("<!--__DIAGRAM__-->", svg)
    html = html.replace("<!--__DEFINITION__-->", define)
    html = html.replace("/*__STEPS__*/[]", steps)
    html = html.replace("__TOPIC__", a.topic)
    html = html.replace("__MODE__", a.mode)

    out = pathlib.Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"생성 완료: {out}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
