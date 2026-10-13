# 신상도역 이안 홈페이지

신상도역 이안(이안 동작) 분양 홍보 홈페이지입니다. 업체가 준 전단·리플렛·이미지를 바탕으로 만들었고,
메뉴 구성은 참고 사이트(https://www.신상도역-이안.com 계열, 주소: `xn----o68eo64ab7bd8di2ai2f.com`)를 따랐습니다.

빌드 도구나 프레임워크 없이 HTML·CSS·JS 만으로 된 정적 사이트라, `site/` 폴더만 어디든 올리면 됩니다.

## 미리 보기

```bash
cd site
python -m http.server 8765
# 브라우저에서 http://127.0.0.1:8765
```

## 폴더 구조

| 경로 | 내용 |
|---|---|
| `site/` | **배포되는 결과물.** `*.html`, `styles.css`, `home.css`, `main.js`, `assets/` |
| `pages/` | 페이지 본문 조각(`index.html`, `intro.html` …)과 공통 헤더·푸터(`_layout.html`) |
| `tools/build_pages.py` | `pages/` → `site/*.html` 을 만든다 |
| `tools/build_assets.py` | 업체 원본 자료 → `site/assets/` 의 웹용 이미지를 만든다 |
| `tools/upscale.py` | 원본을 못 받은 저해상도 사진을 2배로 키운다(인테리어 사진 모음에만 씀, torch·spandrel 필요) |
| `신상도역 이안_랜딩페이지 제작자료/` | 업체 원본(전단·리플렛 PDF, 투시도·조감도·평면 원본). 약 160MB 라 저장소에는 올리지 않는다 |

## 페이지 구성

| 메뉴 | 파일 | 내용 |
|---|---|---|
| 홈 | `index.html` | 히어로, 7개 페이지 안내판, 오시는 길, 관심고객 등록 폼 |
| 사업개요 | `intro.html` | 개요 표, 사업진행 절차 6단계, 상도동 지형 현황 |
| 입지환경 | `location.html` | 광역 지도, 역 안내 기둥, 입지 장점 4가지 |
| 프리미엄 | `premium.html` | 항공 조망, 無조건 BENEFIT 8 |
| 단지안내 | `complex.html` | 조감도, 배치도, 세대수, 단지 사진, 동·호수표 |
| 평면안내 | `type.html` | 59.99 / 59.15 / 71.58 / 84.99 타입 평면도(비확장선 표시 전환) |
| 커뮤니티 | `community.html` | 시설 5곳, 사진 3장, 단지 배치도 |
| 인테리어 | `interior.html` | 인테리어 사진 모음, 옵션품목 |

- 헤더는 두 줄이다. 윗줄(전체 헤더)은 로고·메뉴·전화·등록 버튼, 아랫줄(이동 헤더)은 앞·현재·다음 페이지.
- 메뉴는 지하철 노선도 모양이고, 현재 페이지가 "현재 역"으로 표시된다.
- 서브페이지 맨 아래에는 "다음 페이지" 링크와 등록 버튼이 있다. 등록 폼은 홈에만 있다.

## 고치는 방법

`site/*.html` 은 자동으로 만들어지는 결과물이다. **직접 고치면 다음에 만들 때 덮어쓴다.**

| 고칠 것 | 고칠 곳 | 그다음 |
|---|---|---|
| 페이지 본문 | `pages/<페이지>.html` | `python tools/build_pages.py` |
| 헤더·푸터·`<head>` | `pages/_layout.html` | `python tools/build_pages.py` |
| 메뉴 이름·순서, 페이지 설명글 | `tools/build_pages.py` 의 `MENU` | `python tools/build_pages.py` |
| 스타일·스크립트 | `site/styles.css`, `site/home.css`(홈 전용), `site/main.js` | `python tools/build_pages.py` |
| 이미지 | `tools/build_assets.py` | `python tools/build_assets.py` |

- CSS·JS 만 고쳤을 때도 `build_pages.py` 를 돌려야 한다. 주소 뒤에 붙는 `?v=` 값이 바뀌어야
  방문자 브라우저가 예전 파일을 캐시에서 꺼내 쓰지 않는다.
- `build_pages.py` 는 깨진 링크·없는 이미지·없는 `#앵커`가 있으면 `site/` 를 건드리지 않고 멈춘다.
- `build_assets.py` 는 원본 자료 폴더가 있어야 하고 Pillow, PyMuPDF 가 필요하다(Pillow 11.0, PyMuPDF 1.27 에서 확인).
  일부만 다시 만들 수 있다: `python tools/build_assets.py photos | pdf | units | community | leaflet-photos | logo`

## 이미지

파일명 규칙은 `<쓰이는 페이지>-<내용>-<가로폭>.webp` 이다.

| 파일 | 내용 | 원본 |
|---|---|---|
| `home-hero-*`, `home-hero-mobile-*` | 히어로 투시도(세로 화면용은 하늘을 위로 늘린 것) | 투시도 0416 |
| `home-way-showroom-*`, `home-way-site-*` | 주택홍보관·현장 약도 | 리플렛 PDF 1면 |
| `intro-terrain-*` | 상도동 지형 현황 | 카톡 이미지 `_09` |
| `location-map-*`, `location-map-detail-*` | 광역 지도, 단지 주변 확대 지도 | 리플렛 PDF 2면 |
| `location-stations-*` | 역 안내 기둥(투명 배경) | 전단 PDF 1면 |
| `location-traffic/education/infra/vision-*` | 입지 장점 사진 | 리플렛 PDF 2면 이미지컷 |
| `premium-aerial-*` | 항공 조망 | 카톡 이미지 `_05` |
| `complex-birdseye-*` | 조감도 | 조감도 0416 |
| `complex-siteplan-*`, `complex-dongho-*` | 배치도, 동·호수표 | 리플렛 PDF 2면 |
| `complex-walk-*`, `complex-playground-*` | 산책로·놀이터 사진 | 리플렛 PDF 2면 이미지컷 |
| `type-59a/59b/71/84-*`, `type-*-dotline-*` | 평면도, 비확장 점선 표시본 | `유니트/` 원본 + 리플렛의 실명 라벨 |
| `community-fitness/library/care-*` | 커뮤니티 사진 | 카톡 이미지 `_01` (커뮤니티 보드) |
| `interior-options-*` | 옵션 가전 | 카톡 이미지 `_06` |
| `interior-rooms-*` | 인테리어 사진 모음(거실·주방·방·침실·욕실·드레스룸), 제목 글자는 잘라내고 페이지에서 글로 씀 | `인테리어.avif` → ffmpeg 로 푼 `인테리어.png` → `tools/upscale.py` 로 2배 키운 `인테리어_x2.png` |
| `common-favicon.svg`, `common-logo.svg`, `common-og.jpg` | 탭 아이콘, 로고, 공유 미리보기 | 전단 PDF 의 iaan 로고, 투시도 |

해상도가 낮은 것: 커뮤니티 사진 3장(300~365px), 리플렛 이미지컷 6장(520~580px), 인테리어 사진 모음(955px), 항공 조망(2110px).
지금 크기보다 키우면 뭉개진다.
인테리어 사진 모음만 Real-ESRGAN 으로 2배 키워(1910px) 쓰고 있다. 선명해 보이지만 없던 디테일을 그려 넣은 것이라
벽 질감이 매끈해지고 무늬가 조금 달라진다. 원본을 받으면 `tools/build_assets.py` 에서 원본으로 바꾼다.

## 애니메이션

`main.js` 가 화면에 들어온 `.reveal` 요소에 `.is-in` 을 붙이면 한 번 재생된다. 규칙은 `styles.css` 의 "모션" 블록에 있다.

| 클래스 | 움직임 |
|---|---|
| `reveal` | 아래에서 떠오름 |
| `reveal reveal--wipe` | 그림이 왼쪽부터 걷힘 |
| `reveal reveal--slide` | 오른쪽에서 밀려 들어옴 |
| `reveal reveal--stagger` | 자식들이 차례로 떠오름 |
| `reveal reveal--still` | 안쪽 제목이 어절 단위로 올라옴 |
| `count` | 숫자가 0부터 차오름(정수만) |

- 기기에서 "동작 줄이기"를 켠 사람, 스크립트를 끈 브라우저에서는 애니메이션 없이 처음부터 전부 보인다.
- 스크립트 로딩이 실패해도 4초 뒤에는 전부 보이도록 안전장치가 있다.
- 페이지 전환 효과와 스크롤 연동 효과는 지원하는 브라우저에서만 동작한다.

## 관심고객 등록 폼

**아직 접수처가 연결되어 있지 않다.** 지금은 제출하면 "1555-1554 로 전화 주세요" 안내만 뜬다.

연결하려면:

1. `pages/index.html` 의 `<form id="lead-form" action="">` 에 접수 주소를 넣는다.
2. 접수 서버는 성공했을 때 JSON `{"ok": true}` 를 돌려줘야 한다. 그 외 응답은 실패로 본다.
3. `pages/_layout.html` 맨 위 `Content-Security-Policy` 의 `connect-src`, `form-action` 에 그 주소를 넣는다
   (지금은 Google Apps Script 주소가 들어 있다).
4. `python tools/build_pages.py`

보내는 값: `name`, `phone`, `unit`(관심 타입), `visit_date`, `visit_time`, `agree`, `website`(봇 거르는 빈 칸).

접수 서버 쪽에서 해야 할 것: `website` 값이 있으면 버리기, 이름 길이 제한, 구글 시트에 넣는다면
`= + - @` 로 시작하는 값 앞에 `'` 붙이기(수식 실행 방지).

## 남은 결정

- [ ] **접수처** — 등록 내용을 어디로 받을지(구글 시트 등)
- [ ] **개인정보 수집 주체** — 동의 문구에 들어갈 회사명
- [ ] **도메인** — 정해지면 `_layout.html` 의 `og:image` 를 절대 주소로 바꾼다(카카오톡 공유 미리보기용)
- [ ] **이름 표기** — 지금은 "신상도역 이안". 전단 로고는 "이안 동작"
- [ ] **푸터 사업자 정보** — 사업자등록번호·주소는 자료에 없어 비워 뒀다
- [ ] **광고 문구 확인** — 문구는 전단·리플렛 그대로다("확정분양가", "시세차익", "전세금 안전" 포함)
- [ ] **이미지컷 사용 범위** — 리플렛·커뮤니티 보드의 스톡 사진을 홈페이지에 써도 되는지
- [ ] **인테리어 사진 출처** — `인테리어.avif` 가 이 단지 견본주택 사진인지, 홈페이지에 써도 되는지

## 업체에 요청할 자료

카톡으로 받으면 화질이 깎이니 메일이나 드라이브로 원본(가로 2000px 이상)을 받는다.

꼭 필요한 것
1. 인테리어 사진 원본 — 거실, 주방·식당, 안방, 드레스룸, 욕실, 현관 (5~8장). 지금은 여섯 장을 한데 모은 가로 955px 이미지 한 장을 AI 로 2배 키워 쓰고 있어 크게 보여줄 수 없다.
2. 커뮤니티 사진 원본 3장 또는 커뮤니티 보드의 디자인 원본. 가능하면 어린이집·경로당 이미지.
3. 주택홍보관 실제 사진 — 외관(입구·간판), 내부 1~2장.

있으면 좋은 것
4. 추가 CG — 주간 투시도, 단지 입구(문주), 중앙광장·조경, 어린이놀이터
5. 항공 조망 원본
6. 리플렛 이미지컷 6장의 원본
7. 홍보 영상 또는 드론 영상(홈 히어로용)
8. 타입별 3D(아이소) 평면 CG
9. 시공·시행·신탁·보증사 로고 원본(AI·SVG). 지금 푸터에는 글자로만 들어가 있다.
10. 사업개요 수치 — 대지면적, 연면적, 주차대수, 입주 예정 시기

## 저장소와 배포

- 저장소: https://github.com/Leechanhee123/iaan-dongjak (지금은 public)
- 사이트: https://leechanhee123.github.io/iaan-dongjak/ (GitHub Pages)

Pages 는 `gh-pages` 브랜치를 내보낸다. 이 브랜치에는 `site/` 안의 파일만 들어 있다.

**사이트를 고친 뒤 반영하는 순서**

```bash
python tools/build_pages.py                      # site/*.html 다시 만들기
git add -A && git commit -m "..." && git push    # main 에 올리기
git subtree push --prefix site origin gh-pages   # 사이트에 반영 (1~2분 걸림)
```

마지막 줄을 빼먹으면 저장소만 바뀌고 사이트는 그대로다.

**private 으로 되돌릴 때**

현재 요금제(무료)에서는 private 저장소의 Pages 를 쓸 수 없다. 저장소를 private 으로 바꾸면 위 사이트 주소는 내려간다.
그때는 아래 중 하나로 옮긴다. `site/` 폴더만 올리면 되고, 모든 링크가 상대 경로라 어느 주소에서든 그대로 동작한다.

1. GitHub Pro 로 올린다 — private 그대로 Pages 를 쓸 수 있다.
2. Vercel·Cloudflare Pages·Netlify 에 저장소를 연결한다 — 내보낼 폴더를 `site` 로 지정한다. 빌드 명령은 없다.
3. 일반 웹호스팅(카페24 등)에 `site/` 안의 파일을 그대로 올린다.

## 넣지 않은 것

- 리플렛의 공급가 표·납부 일정·계좌번호(참고 사이트도 싣지 않는다)
- 참고 사이트의 "PREMIUM 7"(자료에 해당 내용이 없다)
- 방문예약 폼의 성별 항목, 별도 방문예약 폼(관심고객 등록 하나로 합쳤다)
