"""pages/ 의 본문 조각 + 공통 레이아웃(pages/_layout.html) -> site/*.html

실행: python tools/build_pages.py
site/*.html 은 결과물이라 직접 고치면 다음 실행 때 덮어쓴다. 고칠 곳은 pages/ 다.
헤더 메뉴·이동 헤더(앞/현재/다음)·'다음' 링크는 아래 MENU 순서에서 나온다.

styles.css / home.css / main.js 를 고쳤을 때도 다시 실행한다. 주소 뒤에 파일 내용으로 만든 ?v= 값을
붙여 두기 때문에, 다시 실행해야 방문자 브라우저가 예전 파일을 캐시에서 꺼내 쓰지 않는다.
"""
import hashlib
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = os.path.join(ROOT, "pages")
OUT = os.path.join(ROOT, "site")
SITE = "신상도역 이안"

# (파일명, 메뉴 이름, 검색·공유용 설명) — 참고 사이트의 카테고리 순서 그대로
MENU = [
    ("intro", "사업개요", "신상도역 이안 사업개요. 서울특별시 동작구 상도동 211-386번지 일원, 4개 동 총 459세대(예정), 10년 후 분양전환 장기일반민간임대주택."),
    ("location", "입지환경", "7호선 상도역·서부선 신상도역(예정) 더블역세권. 여의도·강남·용산과 빠르게 통하는 신상도역 이안 입지환경."),
    ("premium", "프리미엄", "청약제한·전매제한·자격조건 없는 신상도역 이안의 無조건 BENEFIT 8."),
    ("complex", "단지안내", "신상도역 이안 조감도, 단지 배치도, 동·호수표. 4개 동 총 459세대(예정)."),
    ("type", "평면안내", "신상도역 이안 평면안내. 59.99㎡, 59.15㎡, 71.58㎡, 84.99㎡ 타입별 평면도와 면적."),
    ("community", "커뮤니티", "피트니스, 작은도서관, 어린이집, 다함께 돌봄센터, 경로당. 신상도역 이안 커뮤니티 시설."),
    ("interior", "인테리어", "신상도역 이안 인테리어. 거실, 주방, 침실, 욕실, 드레스룸과 옵션품목(시스템 에어컨, 발코니확장, 인덕션, 냉장고, 김치냉장고, 식기세척기, 드럼세탁기, 스타일러)."),
]
HOME_TITLE = f"{SITE} | 동작이 기다린 기회"
HOME_DESCRIPTION = ("동작이 기다린 기회, 안이 다른 아파트 이안. 7호선 상도역·서부선 신상도역(예정) 더블역세권, "
                    "10년 후 분양전환 아파트. 59㎡·71㎡·84㎡ 총 459세대(예정). 대표번호 1555-1554")
# 홈에만 필요한 것: 홈 전용 스타일, 히어로 이미지 미리 받기
HOME_HEAD = """<link rel="stylesheet" href="home.css">
<link rel="preload" as="image" media="(max-aspect-ratio: 4/5)" href="assets/home-hero-mobile-720.webp" imagesrcset="assets/home-hero-mobile-720.webp 720w, assets/home-hero-mobile-1080.webp 1080w" imagesizes="100vw">
<link rel="preload" as="image" media="(min-aspect-ratio: 4/5)" href="assets/home-hero-1600.webp" imagesrcset="assets/home-hero-960.webp 960w, assets/home-hero-1600.webp 1600w, assets/home-hero-2400.webp 2400w" imagesizes="100vw">
"""


def read(name):
    with open(os.path.join(PAGES, name), encoding="utf-8") as f:
        return f.read()


def nav(current):
    """현재 페이지는 aria-current, 그보다 앞선 메뉴는 is-passed(노선색 구간)."""
    items = []
    for i, (slug, name, _) in enumerate(MENU):
        passed = ' class="is-passed"' if current is not None and i < current else ""
        here = ' aria-current="page"' if i == current else ""
        items.append(f'      <li{passed}><a href="{slug}.html"{here}>{name}</a></li>\n')
    return "    <ol>\n" + "".join(items) + "    </ol>\n"


def neighbors(i):
    prev = ("index.html", "홈") if i == 0 else (MENU[i - 1][0] + ".html", MENU[i - 1][1])
    nxt = ("index.html#visit", "오시는 길") if i == len(MENU) - 1 else (MENU[i + 1][0] + ".html", MENU[i + 1][1])
    return prev, nxt


def page_head(i):
    (prev_href, prev_name), (next_href, next_name) = neighbors(i)
    return f"""<header class="page-head">
  <div class="wrap station">
    <a href="{prev_href}">{prev_name}</a>
    <h1>{MENU[i][1]}</h1>
    <a href="{next_href}">{next_name}</a>
  </div>
</header>

"""


def page_foot(i):
    _, (next_href, next_name) = neighbors(i)
    return f"""
<aside class="page-foot" aria-label="다음 안내">
  <div class="wrap page-foot-grid reveal">
    <a class="next-stop" href="{next_href}"><span>다음</span><strong>{next_name}</strong></a>
    <a class="btn cta" href="index.html#register">관심고객 등록</a>
  </div>
</aside>
"""


def render(layout, **slots):
    for key, value in slots.items():
        layout = layout.replace("{{" + key + "}}", value)
    left = re.findall(r"\{\{\w+\}\}", layout)
    if left:
        raise SystemExit(f"채워지지 않은 자리: {left}")
    return layout


def versioned(text):
    """CSS·JS 주소에 내용 해시를 붙인다. 새 HTML 이 캐시된 옛 스크립트와 섞여 화면이 어긋나는 일을 막는다."""
    for name in ("styles.css", "home.css", "main.js"):
        with open(os.path.join(OUT, name), "rb") as f:
            digest = hashlib.sha1(f.read()).hexdigest()[:8]
        text = text.replace(f'"{name}"', f'"{name}?v={digest}"')
    return text


def check_links(pages):
    """내부 링크·이미지·#앵커가 실제로 있는지 확인한다. 하나라도 깨졌으면 site/ 를 쓰기 전에 멈춘다."""
    # site/ 의 실제 파일명(대소문자 그대로). 윈도우에서는 열리고 리눅스 서버에서 404 나는 경우를 잡으려고 직접 비교한다.
    files = set()
    for folder, _, names in os.walk(OUT):
        rel = os.path.relpath(folder, OUT).replace(os.sep, "/")
        files.update(name if rel == "." else f"{rel}/{name}" for name in names)
    broken = []
    for name, text in pages.items():
        refs = re.findall(r'(?:href|src)="([^"]+)"', text)
        for srcset in re.findall(r'(?:srcset|imagesrcset)="([^"]+)"', text):
            refs += [part.split()[0] for part in srcset.split(",")]
        for ref in refs:
            if re.match(r"[a-z][a-z0-9+.-]*:", ref):  # https:, tel:, mailto: 등 바깥 주소
                continue
            path, _, anchor = ref.partition("#")
            target = path.partition("?")[0] or name  # "#register" 처럼 같은 페이지 안의 앵커, ?v= 는 떼고 본다
            if target.endswith(".html"):
                if target not in pages:
                    broken.append(f"{name}: {ref} (없는 페이지)")
                elif anchor and f'id="{anchor}"' not in pages[target]:
                    broken.append(f"{name}: {ref} (없는 앵커)")
            elif target not in files:
                broken.append(f"{name}: {ref} (없는 파일)")
    if broken:
        raise SystemExit("깨진 링크가 있어 site/ 를 그대로 두었습니다:\n  " + "\n  ".join(broken))


def main():
    layout = read("_layout.html")
    pages = {"index.html": render(
        layout, title=HOME_TITLE, description=html.escape(HOME_DESCRIPTION), head=HOME_HEAD,
        nav=nav(None), register="#register", header_class="", page_head="", body=read("index.html"), page_foot="")}
    for i, (slug, name, description) in enumerate(MENU):
        pages[slug + ".html"] = render(
            layout, title=f"{name} | {SITE}", description=html.escape(description), head="",
            # 서브페이지에는 히어로가 없으니 전체 헤더를 처음부터 흰 바탕으로
            nav=nav(i), register="index.html#register", header_class=" is-solid", page_head=page_head(i),
            body=read(slug + ".html"),
            page_foot=page_foot(i))
    pages = {name: versioned(text) for name, text in pages.items()}
    check_links(pages)
    for name, text in pages.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(f"{len(pages)} pages -> site/ :", ", ".join(pages))


if __name__ == "__main__":
    main()
