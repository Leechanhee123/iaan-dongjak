"""제작자료(원본 JPG/PDF) -> site/assets 웹용 에셋 생성.

실행: python tools/build_assets.py   (Pillow, PyMuPDF 필요)
원본이 바뀌면 다시 실행하면 된다. 좌표는 251208 리플렛 / 251217 전단 기준.

파일명 규칙: <쓰이는 페이지>-<내용>-<가로폭>.webp
  home(홈) intro(사업개요) location(입지환경) premium(프리미엄) complex(단지안내)
  type(평면안내) community(커뮤니티) interior(인테리어) common(전 페이지 공통: 로고·파비콘·공유 이미지)
"""
import os
import sys

import fitz
from PIL import Image, ImageDraw, ImageFilter, ImageFont

Image.MAX_IMAGE_PIXELS = None  # 원본 평면도가 9933x7017
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "신상도역 이안_랜딩페이지 제작자료")
OUT = os.path.join(ROOT, "site", "assets")
LABEL_FONT = r"C:\Windows\Fonts\NotoSansKR-VF.ttf"  # 인쇄물과 같은 서체
LABEL_SCALE = 1.15  # 모바일 가독성 때문에 인쇄물보다 조금 키움
LABEL_INK = (55, 61, 65)

# 평면도: 원본 파일명 -> (출력 이름, 리플렛 2면에 배치된 이미지 xref)
UNITS = {"59A": ("59a", 105), "59B": ("59b", 107), "71": ("71", 109), "84": ("84", 111)}


def src(*parts):
    return os.path.join(SRC, *parts)


def save(im, name, widths, quality=82):
    for w in widths:
        w = min(w, im.width)
        out = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)
        path = os.path.join(OUT, f"{name}-{w}.webp")
        out.save(path, "WEBP", quality=quality, method=6)
        print(f"  {os.path.basename(path):28} {out.width}x{out.height}  {os.path.getsize(path) // 1024}KB")


def pdf_clip(page, rect, dpi):
    pm = page.get_pixmap(clip=fitz.Rect(rect), dpi=dpi)
    return Image.frombytes("RGB", (pm.width, pm.height), pm.samples)


def pdf_image_rgba(doc, xref):
    """PDF 에 박혀 있는 그림을 투명 배경째로 꺼낸다 (CMYK -> RGB, 소프트마스크 -> 알파)."""
    pm = fitz.Pixmap(doc, xref)
    if pm.n - pm.alpha > 3:
        pm = fitz.Pixmap(fitz.csRGB, pm)
    pm = fitz.Pixmap(pm, fitz.Pixmap(doc, doc.extract_image(xref)["smask"]))
    return Image.frombytes("RGBA", (pm.width, pm.height), pm.samples)


def content_bbox(im, threshold=236):
    """흰 배경을 뺀 실제 그림 영역."""
    return im.convert("L").point(lambda v: 255 if v < threshold else 0).getbbox()


def extend_sky(im, extra):
    """세로 화면용: 맨 윗줄 하늘색을 위로 늘리고 전단처럼 위쪽을 어둡게."""
    w, h = im.size
    top = im.crop((0, 0, w, 12)).resize((w, 1), Image.BOX).filter(ImageFilter.GaussianBlur(40))
    sky = top.resize((w, extra), Image.BILINEAR)
    fade = Image.linear_gradient("L").resize((w, extra)).point(lambda v: 95 + v * 160 // 255)
    sky = Image.composite(sky, Image.new("RGB", (w, extra), (20, 38, 90)), fade)
    out = Image.new("RGB", (w, h + extra))
    out.paste(sky, (0, 0))
    out.paste(im, (0, extra))
    return out


def build_photos():
    print("photos")
    hero = Image.open(src("신상도 힐스더원 투시도 0416.jpg")).convert("RGB")
    save(hero, "home-hero", [2400, 1600, 960], quality=80)
    save(extend_sky(hero.crop((2590, 0, 5990, hero.height)), 1500), "home-hero-mobile", [1080, 720], quality=78)
    og = hero.crop((900, 500, 7400, 3913)).resize((1200, 630), Image.LANCZOS)
    og.save(os.path.join(OUT, "common-og.jpg"), "JPEG", quality=84, optimize=True)

    save(Image.open(src("신상도 힐스더원 조감도 0416.jpg")).convert("RGB"), "complex-birdseye", [2000, 1000])
    aerial = Image.open(src("KakaoTalk_20251222_135459382_05.jpg")).convert("RGB")
    save(aerial.crop((0, 0, 2110, aerial.height)), "premium-aerial", [2110, 1100])
    options = Image.open(src("KakaoTalk_20251222_135459382_06.jpg")).convert("RGB")
    save(options.crop((140, 225, 1165, 815)), "interior-options", [1025, 640], quality=86)
    terrain = Image.open(src("KakaoTalk_20251222_135459382_09.jpg")).convert("RGB")
    save(terrain.crop((290, 930, 3650, 2500)), "intro-terrain", [2000, 1000])


def build_pdf_crops(leaflet, flyer):
    print("pdf crops")
    # 지도는 흰 바탕인 리플렛 2면에서 뽑는다 (전단 2면 지도는 남색 바탕 위에 얹혀 있어 흰 페이지에 안 맞는다).
    # 확대 지도(detail)는 같은 그림 오른쪽 아래의 상세도 부분.
    save(pdf_clip(leaflet[1], (23.4, 106.5, 584.2, 539.6), 400), "location-map", [2400, 1200], quality=84)
    save(pdf_clip(leaflet[1], (354.4, 370.2, 582.9, 538.3), 600), "location-map-detail", [1600, 800], quality=84)
    # 전단 1면의 역 안내 기둥(상도역·신상도역) 원본 그림: 1면에 박힌 큰 그림 가운데 세로로 길쭉한 것(1376x2121).
    tall = [i for i in flyer[0].get_image_info(xrefs=True) if i["xref"] and i["width"] > 500 and i["height"] > i["width"] * 1.4]
    assert len(tall) == 1, f"역 기둥 그림을 하나로 특정하지 못함: {[(i['xref'], i['width'], i['height']) for i in tall]}"
    signs = pdf_image_rgba(flyer, tall[0]["xref"])
    save(signs.crop(signs.getchannel("A").getbbox()), "location-stations", [480, 240], quality=90)
    save(pdf_clip(leaflet[1], (1212, 107, 1609, 421), 300), "complex-siteplan", [1600, 800])
    save(pdf_clip(leaflet[1], (1276, 444, 1765, 789), 400), "complex-dongho", [2400, 1200], quality=86)
    save(pdf_clip(leaflet[0], (797, 247, 989, 382), 500), "home-way-showroom", [1200, 640], quality=84)
    save(pdf_clip(leaflet[0], (797, 406, 989, 541), 500), "home-way-site", [1200, 640], quality=84)


def plan_labels(doc, page, xref):
    """리플렛의 평면 이미지 위치와 그 위에 얹힌 실명 라벨(pt 좌표)을 돌려준다."""
    info = next(i for i in page.get_image_info(xrefs=True) if i["xref"] == xref)
    box = fitz.Rect(info["bbox"])
    pm = fitz.Pixmap(doc, xref)
    embedded = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
    cx0, cy0, cx1, cy1 = content_bbox(embedded)
    sx, sy = box.width / pm.width, box.height / pm.height
    content = fitz.Rect(box.x0 + cx0 * sx, box.y0 + cy0 * sy, box.x0 + cx1 * sx, box.y0 + cy1 * sy)
    labels = []
    for block in page.get_text("dict", clip=box + (-8, -8, 8, 8))["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["color"] != 0xFFFFFF and span["text"].strip():  # 흰색은 외곽선용 중복
                    labels.append((span["text"].strip(), span["origin"], span["size"], span["bbox"]))
    return content, labels


def build_leaflet_photos(leaflet):
    """리플렛 2면에 박혀 있는 이미지컷 사진 6장. 인쇄용이라 가로 520~580px 뿐이어서 그 크기 그대로 쓴다."""
    print("leaflet photos")
    page = leaflet[1]
    # 이름: 리플렛에서 사진이 놓인 자리의 왼쪽 위 좌표(pt)
    spots = {
        "location-traffic": (151, 558), "location-education": (435, 558),
        "location-infra": (151, 670), "location-vision": (435, 670),
        "complex-walk": (1622, 240), "complex-playground": (1623, 329),
    }
    placed = page.get_image_info(xrefs=True)
    for name, (x, y) in spots.items():
        hits = [i for i in placed if i["xref"] and abs(i["bbox"][0] - x) < 3 and abs(i["bbox"][1] - y) < 3]
        assert len(hits) == 1, f"{name}: 자리 ({x}, {y}) 에서 사진을 하나로 특정하지 못함 ({len(hits)}개)"
        pm = fitz.Pixmap(leaflet, hits[0]["xref"])
        if pm.n - pm.alpha > 3:  # CMYK
            pm = fitz.Pixmap(fitz.csRGB, pm)
        photo = Image.frombytes("RGB", (pm.width, pm.height), pm.samples)
        save(photo, name, [photo.width], quality=88)


def build_community():
    """커뮤니티 보드(카톡 이미지 _01)에 들어 있는 사진 3장을 잘라낸다.

    보드 자체가 작아 사진이 300~370px 밖에 안 된다. 억지로 키우지 않고 그 크기 그대로 저장한다.
    """
    print("community")
    board = Image.open(src("KakaoTalk_20251222_135459382_01.jpg")).convert("RGB")
    photos = {"fitness": (924, 194, 1289, 526), "library": (927, 713, 1224, 880), "care": (1237, 713, 1537, 880)}
    for name, box in photos.items():
        photo = board.crop(box)
        save(photo, f"community-{name}", [photo.width], quality=90)


def build_units(leaflet):
    print("unit plans")
    page = leaflet[1]
    for key, (name, xref) in UNITS.items():
        content, labels = plan_labels(leaflet, page, xref)
        plain = Image.open(src("유니트", f"{key} type.jpg")).convert("RGB")
        dotted = Image.open(src("유니트", f"{key} type_비확장 점선.jpg")).convert("RGB")
        x0, y0, x1, y1 = content_bbox(plain)
        kx, ky = (x1 - x0) / content.width, (y1 - y0) / content.height
        drift = abs(kx / ky - 1)
        print(f"  {key}: {len(labels)} labels, scale {kx:.2f}px/pt, aspect drift {drift:.2%}")
        assert drift < 0.02, f"{key}: 리플렛 평면과 원본 평면의 비율이 다름 - 라벨 위치를 믿을 수 없음"

        pad = round((x1 - x0) * 0.03)
        crop = (max(x0 - pad, 0), max(y0 - pad, 0), min(x1 + pad, plain.width), min(y1 + pad, plain.height))
        for im, suffix in ((plain, ""), (dotted, "-dotline")):
            draw = ImageDraw.Draw(im)
            for text, (ox, oy), size, _ in labels:
                px = size * kx * LABEL_SCALE
                font = ImageFont.truetype(LABEL_FONT, round(px))
                font.set_variation_by_axes([600])
                grow = (LABEL_SCALE - 1) / LABEL_SCALE
                x = x0 + (ox - content.x0) * kx - draw.textlength(text, font=font) * grow / 2
                y = y0 + (oy - content.y0) * ky + px * 0.36 * grow
                draw.text((x, y), text, font=font, fill=LABEL_INK, anchor="ls",
                          stroke_width=round(px * 0.13), stroke_fill="white")
            save(im.crop(crop), f"type-{name}{suffix}", [1800, 900], quality=84)


def build_logo(flyer):
    """전단 1면 우상단의 iaan 로고(벡터)를 SVG path 로 뽑는다."""
    clip = fitz.Rect(480, 28, 550, 58)
    shapes = [d for d in flyer[0].get_drawings()
              if d.get("fill") == (1.0, 1.0, 1.0) and fitz.Rect(d["rect"]).intersects(clip)
              and fitz.Rect(d["rect"]).width < 120]
    assert len(shapes) == 6, f"로고 조각이 6개가 아님: {len(shapes)}"
    box = fitz.Rect()
    for d in shapes:
        box |= d["rect"]
    k = 100 / box.width  # viewBox 폭 100

    def pt(p):
        return f"{(p.x - box.x0) * k:.2f} {(p.y - box.y0) * k:.2f}"

    paths = []
    for d in sorted(shapes, key=lambda d: d["rect"].x0):
        cmds, cur = [], None
        for item in d["items"]:
            if item[0] == "re":
                r = item[1]
                cmds.append(f"M{pt(r.tl)}L{pt(r.tr)}L{pt(r.br)}L{pt(r.bl)}Z")
                cur = None
                continue
            if item[0] == "qu":
                q = item[1]
                cmds.append(f"M{pt(q.ul)}L{pt(q.ur)}L{pt(q.lr)}L{pt(q.ll)}Z")
                cur = None
                continue
            if cur is None or abs(item[1] - cur) > 1e-3:
                cmds.append(f"M{pt(item[1])}")
            if item[0] == "l":
                cmds.append(f"L{pt(item[2])}")
            else:  # 'c' 3차 베지어
                cmds.append(f"C{pt(item[2])} {pt(item[3])} {pt(item[4])}")
            cur = item[-1]
        roof = fitz.Rect(d["rect"]).width > box.width * 0.6
        rule = ' fill-rule="evenodd"' if d.get("even_odd") else ""
        paths.append(f'<path class="{"roof" if roof else "ink"}"{rule} d="{"".join(cmds)}Z"/>')
    h = box.height * k
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 {h:.2f}">'
           '<style>.ink{fill:#004050}.roof{fill:#90c038}</style>' + "".join(paths) + "</svg>")
    with open(os.path.join(OUT, "common-logo.svg"), "w", encoding="utf-8") as f:
        f.write(svg)
    icon = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
            '<style>.ink{fill:#fff}.roof{fill:#90c038}</style><rect width="64" height="64" rx="10" fill="#002c46"/>'
            f'<g transform="translate(6 {32 - h * 0.26:.2f}) scale(.52)">' + "".join(paths) + "</g></svg>")
    with open(os.path.join(OUT, "common-favicon.svg"), "w", encoding="utf-8") as f:
        f.write(icon)
    print(f"common-logo.svg  viewBox 0 0 100 {h:.2f}  {len(svg)}B")


def main():
    os.makedirs(OUT, exist_ok=True)
    pdfs = {("leaflet" if "리플렛" in f else "flyer"): fitz.open(src(f))
            for f in os.listdir(SRC) if f.lower().endswith(".pdf")}
    only = set(sys.argv[1:])
    steps = {
        "photos": build_photos,
        "community": build_community,
        "leaflet-photos": lambda: build_leaflet_photos(pdfs["leaflet"]),
        "pdf": lambda: build_pdf_crops(pdfs["leaflet"], pdfs["flyer"]),
        "units": lambda: build_units(pdfs["leaflet"]),
        "logo": lambda: build_logo(pdfs["flyer"]),
    }
    for name, step in steps.items():
        if not only or name in only:
            step()


if __name__ == "__main__":
    main()
