const TEL = '1555-1554';

/* 관심고객 등록(홈에만 있다) — 아래 다른 기능이 실패해도 접수는 되도록 가장 먼저 건다 */
const leadForm = document.getElementById('lead-form');
if (leadForm) initLeadForm(leadForm);

function initLeadForm(form) {
  const status = form.querySelector('.form-status');
  const submit = form.querySelector('[type="submit"]');
  const FAILED = `접수하지 못했습니다. 잠시 후 다시 시도하시거나 ${TEL}로 전화해 주세요.`;

  function say(state, message) {
    status.dataset.state = state;
    status.textContent = message;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (form.elements.website.value) {
      // 허니팟에 값이 있으면 봇으로 보고 보내지 않는다. 자동완성 탓에 사람이 걸렸을 때를 위해 안내는 남긴다.
      say('error', FAILED);
      return;
    }
    const endpoint = form.getAttribute('action');
    if (!endpoint) {
      say('error', `온라인 접수를 준비하고 있습니다. ${TEL}로 전화 주시면 바로 안내해 드립니다.`);
      return;
    }
    submit.disabled = true;
    say('', '접수하고 있습니다…');
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { Accept: 'application/json' },
        body: new URLSearchParams(new FormData(form)),
        signal: AbortSignal.timeout?.(20000),
      });
      // 접수 서버는 {"ok": true} 를 돌려줘야 한다. 200 이어도 오류 페이지면 저장 실패로 본다.
      const result = response.ok ? await response.json() : null;
      if (!result?.ok) throw new Error(`접수 실패 (HTTP ${response.status})`);
      form.reset();
      say('ok', '등록되었습니다. 담당자가 곧 연락드리겠습니다.');
    } catch {
      say('error', FAILED);
    } finally {
      submit.disabled = false;
    }
  });

  // 오늘 이전 날짜는 고를 수 없게 (기기 현지 날짜 기준)
  const now = new Date();
  form.elements.visit_date.min = new Date(now - now.getTimezoneOffset() * 60000).toISOString().slice(0, 10);
}

/* 모바일 메뉴 */
const header = document.getElementById('site-header');
const route = document.getElementById('route');
const menuToggle = header.querySelector('.menu-toggle');

function setMenu(open) {
  menuToggle.setAttribute('aria-expanded', String(open));
  header.classList.toggle('is-menu-open', open);
}
menuToggle.addEventListener('click', () => setMenu(menuToggle.getAttribute('aria-expanded') !== 'true'));
route.addEventListener('click', (event) => {
  if (event.target.closest('a')) setMenu(false);
});
document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape' || menuToggle.getAttribute('aria-expanded') !== 'true') return;
  setMenu(false);
  menuToggle.focus(); // 닫힌 패널 안에 포커스가 남지 않게
});

/* 홈: 히어로 위에서는 투명, 히어로를 벗어나면 흰 배경. (서브페이지 헤더는 처음부터 흰 배경이라 해당 없음) */
const heroStage = document.querySelector('.hero-stage');
if (heroStage) {
  new IntersectionObserver(
    ([entry]) => header.classList.toggle('is-solid', !entry.isIntersecting),
    { rootMargin: `-${header.offsetHeight}px 0px 0px 0px` },
  ).observe(heroStage);
}

/* 등장 애니메이션 — 어떤 클래스가 어떻게 움직이는지는 styles.css 의 '모션' 참고.
   '동작 줄이기' 설정이면 아무것도 하지 않는다 (그때는 CSS 도 처음부터 전부 보여 준다). */
if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {
  // 제목을 어절 단위로 감싼다: <span class="w"><span>어절</span></span>
  const splitWords = (el) => {
    // 화면 낭독기가 어절마다 끊어 읽지 않도록, 제목은 원래 문장을 이름표로 달고 조각들은 가린다
    const isHeading = /^H[1-6]$/.test(el.tagName);
    if (isHeading) el.setAttribute('aria-label', el.innerText.replace(/\s+/g, ' ').trim());
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    const textNodes = [];
    while (walker.nextNode()) textNodes.push(walker.currentNode);
    let index = 0;
    for (const node of textNodes) {
      const pieces = node.textContent.split(/(\s+)/).filter(Boolean).map((piece) => {
        if (!piece.trim()) return ' ';
        const word = document.createElement('span');
        const inner = document.createElement('span');
        word.className = 'w';
        if (isHeading) word.setAttribute('aria-hidden', 'true');
        inner.textContent = piece;
        inner.style.setProperty('--i', index++);
        word.append(inner);
        return word;
      });
      node.replaceWith(...pieces);
    }
    el.classList.add('split');
  };
  // 등장 대상(.reveal) 안에 있는 제목만 쪼갠다. 밖에 있는 제목은 올려 줄 계기가 없어 숨은 채로 남는다.
  document.querySelectorAll('.hero h1, main h2, .first-last, .block-title').forEach((el) => {
    if (el.closest('.reveal')) splitWords(el);
  });

  // 차례로 등장할 자식들에 순번을 매긴다
  document.querySelectorAll('.reveal--stagger').forEach((box) => {
    [...box.children].forEach((child, i) => child.style.setProperty('--i', i));
  });

  // 숫자가 0 부터 차오른다
  const countUp = (el) => {
    const target = Number(el.textContent);
    if (el.dataset.counted || !Number.isFinite(target)) return;
    el.dataset.counted = 'true';
    el.style.minWidth = `${el.textContent.length}ch`; // 자릿수가 늘어나는 동안 옆 글자가 밀리지 않게
    const began = performance.now();
    const tick = (now) => {
      const progress = Math.min((now - began) / 1500, 1);
      el.textContent = Math.round(target * (1 - (1 - progress) ** 4));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  };
  // 숫자는 그 숫자를 싣고 등장하는 요소의 움직임이 실제로 시작될 때 센다.
  // (등장에 지연이 걸려 있으면 그만큼 기다려야, 보이기도 전에 다 세어 버리지 않는다)
  const CARRIER = '.reveal--stagger > *, .reveal--still > *, .reveal';
  document.addEventListener('animationstart', (event) => {
    event.target.querySelectorAll('.count').forEach((el) => {
      if (el.closest(CARRIER) === event.target) countUp(el);
    });
  });

  // 화면에 들어온 것부터 등장. 한꺼번에 들어온 것들은 0.09초 간격으로 차례를 둔다.
  const seen = new IntersectionObserver((entries) => {
    let order = 0;
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      const el = entry.target;
      el.style.setProperty('--d', `${order++ * 90}ms`);
      el.classList.add('is-in');
      seen.unobserve(el);
    }
  }, { rootMargin: '0px 0px -6% 0px', threshold: 0.05 });
  document.querySelectorAll('.reveal').forEach((el) => seen.observe(el));

  // 여기까지 왔으면 준비 끝: CSS 의 4초 안전장치를 끄고 대기 상태로 둔다
  document.documentElement.classList.add('io');
}
