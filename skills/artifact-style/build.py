#!/usr/bin/env python3
import argparse
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STYLE_VERSION = "1"
FONTS = "https://fonts.googleapis.com/css2?family=Do+Hyeon&family=Noto+Sans+KR:wght@400;500;700;900&family=JetBrains+Mono:wght@400;600&display=swap"
SLUG = re.compile(r"^[a-z][a-z0-9-]*$")
# claude.ai가 주소 해시로 예약한 이름
RESERVED_IDS = {"settings", "sidebar", "customize", "upgrade", "downloads"}
LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
HINT = "맞는 컴포넌트가 없으면 SKILL.md 「컴포넌트 추가」 절차로 라이브러리에 추가"

errors = []


def fail(path, msg):
    errors.append(f"{path}: {msg}")


def plain(s):
    return re.sub(r"\*\*|==|__|`", "", LINK.sub(r"\1", s))


def emphasis(t):
    t = html.escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)
    return re.sub(r"__(.+?)__", r"<u>\1</u>", t)


# 글자는 모두 이스케이프한 뒤 정해진 표기만 태그로 변환 (임의 HTML 차단), 코드와 링크 주소는 강조 표기 변환 제외
def inline(s):
    out = []
    for part in re.split(r"(`[^`]+`|\[[^\]]+\]\(https?://[^)\s]+\))", s):
        if len(part) > 2 and part[0] == part[-1] == "`":
            out.append(f"<code>{html.escape(part[1:-1])}</code>")
        elif (m := LINK.fullmatch(part)):
            out.append(f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{emphasis(m.group(1))}</a>')
        else:
            out.append(emphasis(part))
    return "".join(out)


def keys(obj, path, required, optional=()):
    if not isinstance(obj, dict):
        fail(path, "객체여야 함")
        return {}
    for k in required:
        if k not in obj:
            fail(path, f"{k} 필요")
    for k in obj:
        if k not in required and k not in optional:
            fail(path, f"모르는 항목 {k}. {HINT}")
    return obj


def text(v, path, limit):
    if not isinstance(v, str) or not v.strip():
        fail(path, "비어 있지 않은 글자여야 함")
        return ""
    n = len(plain(v))
    if n > limit:
        fail(path, f"{n}자, {limit}자 이하로 줄이거나 details로 접기")
    return inline(v)


# 태그가 들어갈 수 없는 자리(탭 제목, 입력창 안내)용, 표기 변환 없이 이스케이프만
def raw(v, path, limit):
    text(v, path, limit)
    return html.escape(v) if isinstance(v, str) else ""


def items(v, path, lo, hi):
    if not isinstance(v, list):
        fail(path, f"{lo}~{hi}개 목록이어야 함")
        return []
    if not lo <= len(v) <= hi:
        fail(path, f"{len(v)}개, {lo}~{hi}개여야 함")
    return v


def choice(v, path, allowed):
    if v not in allowed:
        fail(path, f"{', '.join(allowed)} 중 하나여야 함")
        return allowed[0]
    return v


def url(v, path):
    if not isinstance(v, str) or not re.match(r"^https?://\S+$", v):
        fail(path, "http(s) 주소여야 함")
        return "#"
    return html.escape(v)


def b_answer(b, p, ctx):
    keys(b, p, ["text"])
    return f'<p class="answer">{text(b.get("text"), p + ".text", 120)}</p>'


def b_text(b, p, ctx):
    keys(b, p, ["text"])
    return f'<p>{text(b.get("text"), p + ".text", 220)}</p>'


def b_note(b, p, ctx):
    keys(b, p, ["text"])
    return f'<p class="muted">{text(b.get("text"), p + ".text", 200)}</p>'


def b_meter(b, p, ctx):
    keys(b, p, ["percent", "label"])
    pct = b.get("percent")
    if not isinstance(pct, (int, float)) or isinstance(pct, bool) or not 0 <= pct <= 100:
        fail(p + ".percent", "0~100 숫자여야 함")
        pct = 0
    label = text(b.get("label"), p + ".label", 60)
    return f'<div class="meter"><div class="meter-track" role="img" aria-label="{html.escape(plain(b.get("label") or ""))}"><i style="width:{pct:g}%"></i></div><small>{label}</small></div>'


def b_points(b, p, ctx):
    keys(b, p, ["items"])
    hi, limit = (8, 200) if ctx["in_details"] else (3, 100)
    lis = "".join(f"<li>{text(t, f'{p}.items[{i}]', limit)}</li>" for i, t in enumerate(items(b.get("items"), p + ".items", 1, hi)))
    return f'<ul class="pts">{lis}</ul>'


def b_box(b, p, ctx):
    keys(b, p, ["tone", "title", "text"])
    tone = choice(b.get("tone"), p + ".tone", ["red", "warn", "good"])
    return f'<div class="box {tone}"><b>{text(b.get("title"), p + ".title", 30)}</b><span>{text(b.get("text"), p + ".text", 200)}</span></div>'


def b_details(b, p, ctx):
    keys(b, p, ["summary", "blocks"])
    if ctx["in_details"]:
        fail(p, "details 안에 details 금지")
    ctx["in_details"] = True
    inner = "\n".join(block(x, f"{p}.blocks[{i}]", ctx) for i, x in enumerate(items(b.get("blocks"), p + ".blocks", 1, 6)))
    ctx["in_details"] = False
    return f'<details><summary>더 보기: {text(b.get("summary"), p + ".summary", 60)}</summary><div>{inner}</div></details>'


def b_nums(b, p, ctx):
    keys(b, p, ["items"])
    out = []
    for i, it in enumerate(items(b.get("items"), p + ".items", 2, 4)):
        q = f"{p}.items[{i}]"
        it = keys(it, q, ["value", "label"])
        out.append(f'<div class="num"><strong>{text(it.get("value"), q + ".value", 14)}</strong><small>{text(it.get("label"), q + ".label", 60)}</small></div>')
    return f'<div class="nums">{"".join(out)}</div>'


def b_steps(b, p, ctx):
    keys(b, p, ["items"])
    lis = "".join(f"<li><span>{text(t, f'{p}.items[{i}]', 140)}</span></li>" for i, t in enumerate(items(b.get("items"), p + ".items", 2, 6)))
    return f'<ol class="steps">{lis}</ol>'


def b_formula(b, p, ctx):
    keys(b, p, ["items"])
    out = []
    for i, it in enumerate(items(b.get("items"), p + ".items", 2, 4)):
        q = f"{p}.items[{i}]"
        it = keys(it, q, ["title", "text"])
        out.append(f'<div class="f"><b>{text(it.get("title"), q + ".title", 12)}</b><span>{text(it.get("text"), q + ".text", 120)}</span></div>')
    return f'<div class="formula">{"".join(out)}</div>'


def cell(c, p):
    if isinstance(c, dict):
        c = keys(c, p, ["tag", "text"], ["note"])
        tone = choice(c.get("tag"), p + ".tag", ["ok", "chk", "no"])
        note = f' {text(c["note"], p + ".note", 100)}' if "note" in c else ""
        return f'<span class="tag {tone}">{text(c.get("text"), p + ".text", 16)}</span>{note}'
    return text(c, p, 120)


def b_table(b, p, ctx):
    keys(b, p, ["columns", "rows"])
    cols = items(b.get("columns"), p + ".columns", 2, 5)
    head = "".join(f"<th>{text(c, f'{p}.columns[{i}]', 20)}</th>" for i, c in enumerate(cols))
    rows = []
    for r, row in enumerate(items(b.get("rows"), p + ".rows", 1, 30)):
        q = f"{p}.rows[{r}]"
        if not isinstance(row, list) or len(row) != len(cols):
            fail(q, f"칸 수가 열 수({len(cols)})와 같아야 함")
            continue
        rows.append("<tr>" + "".join(f"<td>{cell(c, f'{q}[{i}]')}</td>" for i, c in enumerate(row)) + "</tr>")
    return f'<div class="tbl"><table><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def b_rank(b, p, ctx):
    keys(b, p, ["items"])
    out = []
    for i, it in enumerate(items(b.get("items"), p + ".items", 2, 10)):
        q = f"{p}.items[{i}]"
        it = keys(it, q, ["value", "text"])
        out.append(f'<div class="rank-row"><span class="v">{text(it.get("value"), q + ".value", 10)}</span><span>{text(it.get("text"), q + ".text", 120)}</span></div>')
    return f'<div class="rank">{"".join(out)}</div>'


def b_code(b, p, ctx):
    keys(b, p, ["text"])
    t = b.get("text")
    if not isinstance(t, str) or not t.strip():
        fail(p + ".text", "비어 있지 않은 글자여야 함")
        t = ""
    elif t.count("\n") >= 30:
        fail(p + ".text", "30줄 이하여야 함")
    return f"<pre><code>{html.escape(t)}</code></pre>"


def b_checklist(b, p, ctx):
    keys(b, p, ["items"])
    ctx["scripts"].add("check")
    out = []
    for i, t in enumerate(items(b.get("items"), p + ".items", 1, 5)):
        ctx["check_n"] += 1
        cid = f"t{ctx['check_n']}"
        out.append(f'<label for="{cid}"><input type="checkbox" id="{cid}"><span>{text(t, f"{p}.items[{i}]", 100)}</span></label>')
    return f'<div class="check">{"".join(out)}</div>'


def b_copy(b, p, ctx):
    keys(b, p, ["items"])
    ctx["scripts"].add("copy")
    out = []
    for i, it in enumerate(items(b.get("items"), p + ".items", 1, 10)):
        q = f"{p}.items[{i}]"
        it = keys(it, q, ["label", "text"])
        out.append(f'<div class="copy-item"><div><small>{text(it.get("label"), q + ".label", 40)}</small><q>{text(it.get("text"), q + ".text", 300)}</q></div><button class="copy-btn" type="button">복사</button></div>')
    return f'<div class="copy-list">{"".join(out)}</div>'


BLOCKS = {
    "answer": b_answer, "text": b_text, "note": b_note, "points": b_points, "box": b_box, "details": b_details,
    "nums": b_nums, "steps": b_steps, "formula": b_formula, "table": b_table, "rank": b_rank,
    "code": b_code, "checklist": b_checklist, "copy": b_copy, "meter": b_meter,
}


def block(b, p, ctx):
    kind = b.get("type") if isinstance(b, dict) else None
    if kind not in BLOCKS:
        fail(p, f"type은 {', '.join(BLOCKS)} 중 하나. {HINT}")
        return ""
    return BLOCKS[kind]({k: v for k, v in b.items() if k != "type"}, p, ctx)


def section(s, p, ctx):
    s = keys(s, p, ["id", "nav", "eyebrow", "title", "blocks"])
    sid = s.get("id")
    if not isinstance(sid, str) or not SLUG.match(sid) or sid in RESERVED_IDS or sid.startswith("comment-"):
        fail(p + ".id", "영어 소문자, 숫자, 하이픈만 (settings 등 예약어 제외)")
        sid = "x"
    elif sid in ctx["ids"]:
        fail(p + ".id", f"{sid} 중복")
    ctx["ids"].add(sid)
    ctx["nav"].append((sid, text(s.get("nav"), p + ".nav", 10)))
    blocks = items(s.get("blocks"), p + ".blocks", 1, 7)
    kinds = [b.get("type") for b in blocks if isinstance(b, dict)]
    for k in ("answer", "text"):
        if kinds.count(k) > 1:
            fail(p + ".blocks", f"{k}는 단락 바깥에 1개까지, 나머지는 details로 접기")
    body = "\n".join(block(b, f"{p}.blocks[{i}]", ctx) for i, b in enumerate(blocks))
    return (f'<section id="{sid}">\n<span class="eyebrow">{text(s.get("eyebrow"), p + ".eyebrow", 30)}</span>\n'
            f'<h2>{text(s.get("title"), p + ".title", 40)}</h2>\n{body}\n</section>')


def footer(v):
    spans = "".join(f"<span>{text(t, f'footer[{i}]', 220)}</span>" for i, t in enumerate(items(v, "footer", 1, 4)))
    return f"<footer>{spans}</footer>"


def doc(page, ctx):
    keys(page, "page", ["layout", "audience", "title", "eyebrow", "h1", "hero", "sections", "footer"], ["lead", "intro"])
    hero = keys(page.get("hero"), "hero", ["items"], ["eyebrow", "text"])
    hero_items = "".join(f"<li>{text(t, f'hero.items[{i}]', 50)}</li>" for i, t in enumerate(items(hero.get("items"), "hero.items", 3, 4)))
    hero_eyebrow = text(hero["eyebrow"], "hero.eyebrow", 30) if "eyebrow" in hero else "1분 요약 · 이것만 기억하세요"
    hero_text = f'<p>{text(hero["text"], "hero.text", 160)}</p>' if "text" in hero else ""
    sections = "\n\n".join(section(s, f"sections[{i}]", ctx) for i, s in enumerate(items(page.get("sections"), "sections", 1, 10)))
    lead = f'<p class="muted">{text(page["lead"], "lead", 80)}</p>' if "lead" in page else ""
    if "intro" in ctx:
        lead = f'<p class="intro">{ctx["intro"]}</p>\n' + lead
    nav = "".join(f'<a href="#{sid}">{label}</a>' for sid, label in ctx["nav"])
    return f'''<div class="wrap">

<header>
<span class="eyebrow">{text(page.get("eyebrow"), "eyebrow", 50)}</span>
<h1>{text(page.get("h1"), "h1", 30)}</h1>
{lead}
<nav aria-label="바로가기">{nav}</nav>
</header>

<section class="hero" aria-label="1분 요약">
<span class="eyebrow">{hero_eyebrow}</span>
<ol>{hero_items}</ol>
{hero_text}
</section>

{sections}

{footer(page.get("footer"))}

</div>'''


def card(c, p):
    c = keys(c, p, ["name", "one"], ["badges", "info", "links"])
    badges = ""
    for i, bd in enumerate(items(c.get("badges", []), p + ".badges", 0, 5)):
        q = f"{p}.badges[{i}]"
        bd = keys(bd, q, ["text", "tone"])
        tone = choice(bd.get("tone"), q + ".tone", ["accent", "line", "ok", "warn", "new"])
        badges += f'<span class="b {tone}">{text(bd.get("text"), q + ".text", 16)}</span>'
    info = ""
    for i, pair in enumerate(items(c.get("info", []), p + ".info", 0, 6)):
        q = f"{p}.info[{i}]"
        if not isinstance(pair, list) or len(pair) != 2:
            fail(q, "[이름, 내용] 두 칸이어야 함")
            continue
        info += f"<dt>{text(pair[0], q + '[0]', 6)}</dt><dd>{text(pair[1], q + '[1]', 160)}</dd>"
    links = ""
    for i, ln in enumerate(items(c.get("links", []), p + ".links", 0, 4)):
        q = f"{p}.links[{i}]"
        ln = keys(ln, q, ["text", "url"])
        links += f'<a href="{url(ln.get("url"), q + ".url")}" target="_blank" rel="noopener">{text(ln.get("text"), q + ".text", 20)}</a>'
    return (f'<article class="card"><div class="card-top"><span class="card-name">{text(c.get("name"), p + ".name", 40)}</span>{badges}</div>'
            f'<p class="card-one">{text(c.get("one"), p + ".one", 120)}</p>'
            + (f'<dl class="info">{info}</dl>' if info else "")
            + (f'<div class="card-links">{links}</div>' if links else "")
            + "</article>")


def catalog(page, ctx):
    keys(page, "page", ["layout", "audience", "title", "h1", "summary", "groups", "footer"], ["eyebrow", "lead", "search", "intro"])
    ctx["scripts"].add("search")
    sums = ""
    for i, it in enumerate(items(page.get("summary"), "summary", 2, 4)):
        q = f"summary[{i}]"
        it = keys(it, q, ["value", "label"])
        sums += f'<div class="sum"><b>{text(it.get("value"), q + ".value", 12)}</b><span>{text(it.get("label"), q + ".label", 20)}</span></div>'
    groups = ""
    for g, grp in enumerate(items(page.get("groups"), "groups", 1, 20)):
        q = f"groups[{g}]"
        grp = keys(grp, q, ["title", "cards"])
        cards = items(grp.get("cards"), q + ".cards", 1, 60)
        inner = "".join(card(c, f"{q}.cards[{i}]") for i, c in enumerate(cards))
        groups += f'<div class="group"><div class="group-title"><h2>{text(grp.get("title"), q + ".title", 20)}</h2><small>{len(cards)}개</small></div><div class="cards">{inner}</div></div>'
    eyebrow = f'<span class="eyebrow">{text(page["eyebrow"], "eyebrow", 50)}</span>' if "eyebrow" in page else ""
    lead = f'<p class="muted">{text(page["lead"], "lead", 80)}</p>' if "lead" in page else ""
    if "intro" in ctx:
        lead = f'<p class="intro">{ctx["intro"]}</p>\n' + lead
    search = raw(page["search"], "search", 40) if "search" in page else "이름이나 쓰임으로 찾기"
    return f'''<div class="wrap wide">

<header>
{eyebrow}
<h1>{text(page.get("h1"), "h1", 30)}</h1>
{lead}
</header>

<div class="summary">{sums}</div>

<div class="bar" role="search"><input id="q" type="search" placeholder="{search}" aria-label="찾기"></div>

{groups}

<p class="empty" id="empty" hidden>찾는 항목이 없어요. 검색어를 바꿔 보세요.</p>

{footer(page.get("footer"))}

</div>'''


SCRIPTS = {
    # 체크 상태는 보는 사람 브라우저에만 저장, 저장 불가여도 페이지는 정상 표시
    "check": """document.querySelectorAll('.check input').forEach(function(el){
  try{ if(localStorage.getItem('todo-'+el.id)==='1') el.checked=true; }catch(e){}
  el.addEventListener('change',function(){ try{ localStorage.setItem('todo-'+el.id, el.checked?'1':'0'); }catch(e){} });
});""",
    # 클립보드 거부 시 글자 선택으로 대체
    "copy": """document.querySelectorAll('.copy-btn').forEach(function(btn){
  btn.addEventListener('click',function(){
    var q=btn.parentElement.querySelector('q');
    function done(){btn.textContent='복사됨';setTimeout(function(){btn.textContent='복사'},1500)}
    function pick(){var r=document.createRange();r.selectNodeContents(q);var s=getSelection();s.removeAllRanges();s.addRange(r);btn.textContent='선택됨'}
    try{navigator.clipboard.writeText(q.textContent).then(done,pick)}catch(e){pick()}
  });
});""",
    "search": """(function(){
  var q=document.getElementById('q'), empty=document.getElementById('empty');
  q.addEventListener('input',function(){
    var w=q.value.trim().toLowerCase(), any=false;
    document.querySelectorAll('.group').forEach(function(g){
      var n=0;
      g.querySelectorAll('.card').forEach(function(c){ var hit=!w||c.textContent.toLowerCase().indexOf(w)>=0; c.hidden=!hit; if(hit)n++; });
      g.hidden=n===0; if(n)any=true;
    });
    empty.hidden=any;
  });
})();""",
}


# 링크만 받은 사람은 대화 맥락이 없어 무슨 문서인지 첫머리 설명 필수
def audience(page, ctx):
    who = choice(page.get("audience"), "audience", ["self", "shared"])
    intro = page.get("intro")
    if who == "shared":
        if intro is None:
            fail("intro", "shared 문서는 무슨 문서이고 누가 읽으면 좋은지 intro로 설명 (120자)")
        else:
            ctx["intro"] = text(intro, "intro", 120)
    elif intro is not None:
        ctx["intro"] = text(intro, "intro", 120)


def build(page):
    ctx = {"in_details": False, "ids": set(), "nav": [], "scripts": set(), "check_n": 0}
    if not isinstance(page, dict):
        fail("page", "객체여야 함")
        return ""
    layout = choice(page.get("layout"), "layout", ["doc", "catalog"])
    audience(page, ctx)
    body = doc(page, ctx) if layout == "doc" else catalog(page, ctx)
    title = raw(page.get("title"), "title", 20)
    css = (HERE / "style.css").read_text(encoding="utf-8")
    scripts = "\n".join(SCRIPTS[k] for k in sorted(ctx["scripts"]))
    return (f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n'
            f'<meta name="artifact-style" content="{STYLE_VERSION}">\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="{FONTS}">\n'
            f"<style>\n{css}</style>\n\n{body}\n"
            + (f"\n<script>\n{scripts}\n</script>\n" if scripts else ""))


def main():
    ap = argparse.ArgumentParser(description="artifact-style 페이지 JSON을 검사하고 HTML로 변환")
    ap.add_argument("page", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    args = ap.parse_args()
    try:
        page = json.loads(args.page.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        sys.exit(f"페이지 파일을 읽지 못함: {e}")
    out = build(page)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"형식 오류 {len(errors)}개, HTML을 만들지 않음")
    dest = args.out or args.page.with_suffix(".html")
    dest.write_text(out, encoding="utf-8")
    print(dest)


if __name__ == "__main__":
    main()
