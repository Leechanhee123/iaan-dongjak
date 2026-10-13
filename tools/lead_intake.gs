/**
 * 신상도역 이안 관심고객 접수 — 구글 스프레드시트에 붙여 쓰는 Apps Script.
 *
 * 홈의 등록 폼(pages/index.html 의 #lead-form)이 보낸 값을 이 스프레드시트의 '접수' 시트에 한 줄씩 쌓는다.
 * 설치·배포 순서는 README 의 "관심고객 등록 폼" 참고.
 * 코드를 고친 뒤에는 배포 > 배포 관리 > 수정 > 버전 "새 버전" 으로 다시 배포해야 반영된다(주소는 그대로).
 */
const SHEET_NAME = '접수';
const HEADERS = ['접수시각', '성함', '연락처', '관심 타입', '방문 희망일', '방문 시간대', '개인정보 동의'];
const UNITS = ['59.99', '59.15', '71.58', '84.99', '미정'];
const TIMES = ['오전', '오후'];
const DEDUPE_SECONDS = 600; // 똑같은 접수가 다시 오면(전송이 늦어 다시 누른 경우) 10분 동안은 한 번만 적는다
const MAX_PER_MINUTE = 30; // 이보다 몰리면 장난으로 보고 거절한다. 폼은 "전화 주세요" 안내로 넘어간다

function doPost(e) {
  try {
    const p = e.parameter;
    if (p.website) return json_({ ok: true }); // 허니팟: 봇에게는 된 것처럼 답하고 버린다
    const lead = parseLead_(p);
    if (!lead) return json_({ ok: false });

    const cache = CacheService.getScriptCache();
    // ponytail: 캐시 카운터는 동시에 들어오면 덜 세는 대략적인 한도다. 실제로 도배를 당하면 reCAPTCHA 같은 확인 절차로 바꾼다
    const minute = 'n' + Math.floor(Date.now() / 60000);
    const count = Number(cache.get(minute)) + 1;
    if (count > MAX_PER_MINUTE) return json_({ ok: false });
    cache.put(minute, String(count), 120);

    const row = [lead.name, lead.phone, lead.unit, lead.date, lead.time];
    const key = row.join('|');
    if (!cache.get(key)) {
      sheet_().appendRow([new Date(), ...row, '동의']);
      cache.put(key, '1', DEDUPE_SECONDS);
    }
    return json_({ ok: true });
  } catch (error) {
    console.error(error);
    return json_({ ok: false });
  }
}

/** 배포 주소를 브라우저로 열었을 때 살아 있는지 보여준다. */
function doGet() {
  return json_({ ok: true, service: '신상도역 이안 관심고객 접수' });
}

/** 폼 값을 검사해 시트에 적을 값으로 다듬는다. 받을 수 없는 접수면 null. */
function parseLead_(p) {
  // 시트는 = + - @ 로 시작하는 값을 수식으로 실행하므로 맨 앞에서 떼어 낸다. 제어문자도 지운다
  const name = String(p.name || '').replace(/[\u0000-\u001f\u007f]/g, '').replace(/^[=+\-@\s]+/, '').trim().slice(0, 30);
  const phone = String(p.phone || '').replace(/\D/g, '').match(/^(02|0\d{2})(\d{3,4})(\d{4})$/);
  if (!name || !phone || p.agree !== '동의') return null;
  return {
    name,
    phone: phone.slice(1).join('-'),
    unit: UNITS.includes(p.unit) ? p.unit : '미정',
    date: /^\d{4}-\d{2}-\d{2}$/.test(p.visit_date) ? p.visit_date : '',
    time: TIMES.includes(p.visit_time) ? p.visit_time : '',
  };
}

/** '접수' 시트. 없으면 머리글과 서식을 갖춰 만든다. */
function sheet_() {
  const book = SpreadsheetApp.getActiveSpreadsheet();
  let sheet = book.getSheetByName(SHEET_NAME);
  if (!sheet) {
    book.setSpreadsheetTimeZone('Asia/Seoul');
    sheet = book.insertSheet(SHEET_NAME, 0);
    sheet.appendRow(HEADERS);
    sheet.setFrozenRows(1);
    sheet.getRange('A:A').setNumberFormat('yyyy-mm-dd hh:mm:ss');
    sheet.getRange('B:G').setNumberFormat('@'); // 글자 그대로: 전화번호 앞자리 0 이 지워지지 않게
  }
  return sheet;
}

function json_(body) {
  return ContentService.createTextOutput(JSON.stringify(body)).setMimeType(ContentService.MimeType.JSON);
}

/** 검사 로직 점검. Apps Script 편집기에서 selfTest 를 골라 실행한다(시트는 건드리지 않는다). */
function selfTest() {
  const form = { name: '홍길동', phone: '010-1234-5678', unit: '84.99', visit_date: '2026-11-01', visit_time: '오후', agree: '동의' };
  const eq = (got, want) => {
    if (JSON.stringify(got) !== JSON.stringify(want)) throw new Error(`기대 ${JSON.stringify(want)} / 실제 ${JSON.stringify(got)}`);
  };
  eq(parseLead_(form), { name: '홍길동', phone: '010-1234-5678', unit: '84.99', date: '2026-11-01', time: '오후' });
  eq(parseLead_({ ...form, phone: '02 123 4567' }).phone, '02-123-4567');
  eq(parseLead_({ ...form, phone: '0311234567' }).phone, '031-123-4567');
  eq(parseLead_({ ...form, phone: '01112345678' }).phone, '011-1234-5678');
  eq(parseLead_({ ...form, name: ' =HYPERLINK("x") ' }).name, 'HYPERLINK("x")');
  eq(parseLead_({ ...form, name: '가'.repeat(40) }).name.length, 30);
  eq(parseLead_({ name: '홍길동', phone: '01012345678', unit: '999', visit_date: '내일', visit_time: '밤', agree: '동의' }),
    { name: '홍길동', phone: '010-1234-5678', unit: '미정', date: '', time: '' });
  eq(parseLead_({ ...form, phone: '1234' }), null);
  eq(parseLead_({ ...form, name: ' ' }), null);
  eq(parseLead_({ ...form, agree: '' }), null);
  console.log('selfTest 통과');
}
