#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 CSV 데이터로 월별 검색량 비교 차트 HTML 생성
- 타임라인 필터 (1년 / 6개월 / 3개월)
- 섹션별 엑셀 다운로드
- 카테고리별 사용 키워드 표
"""

import csv
import json
import os
import glob
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")

SAMSUNG_COLOR = "#1428A0"
LG_COLOR      = "#A50034"
COWAY_COLOR   = "#00A651"

BRAND_COLORS = {"삼성": SAMSUNG_COLOR, "LG": LG_COLOR, "코웨이": COWAY_COLOR}

# ── 키워드 정의 ────────────────────────────────────────────────────

TREND_KEYWORDS = {
    "냉장고":    {"삼성": ["삼성냉장고","삼성 냉장고","비스포크냉장고","비스포크 냉장고","삼성 냉장고 추천"],
                  "LG":  ["LG냉장고","LG 냉장고","오브제냉장고","LG 오브제 냉장고","LG 냉장고 추천"]},
    "세탁기":    {"삼성": ["삼성세탁기","삼성 세탁기","비스포크세탁기","비스포크 세탁기","삼성 그랑데"],
                  "LG":  ["LG세탁기","LG 세탁기","LG트롬","LG 트롬 세탁기","트롬세탁기"]},
    "에어컨":    {"삼성": ["삼성에어컨","삼성 에어컨","무풍에어컨","비스포크에어컨","비스포크 에어컨"],
                  "LG":  ["LG에어컨","LG 에어컨","휘센에어컨","LG휘센","LG 휘센 에어컨"]},
    "TV":        {"삼성": ["삼성TV","삼성 TV","네오QLED","삼성 네오QLED","삼성 QLED"],
                  "LG":  ["LGTV","LG TV","LG OLED","LG 올레드","LG OLED TV"]},
    "건조기":    {"삼성": ["삼성건조기","삼성 건조기","비스포크건조기","비스포크 건조기","삼성 그랑데 건조기"],
                  "LG":  ["LG건조기","LG 건조기","LG트롬건조기","LG 트롬 건조기","트롬건조기"]},
    "정수기":    {"삼성": ["삼성정수기","삼성 정수기","비스포크정수기","비스포크 정수기","삼성 정수기 렌탈"],
                  "LG":  ["LG정수기","LG 정수기","퓨리케어정수기","LG 퓨리케어","LG 정수기 렌탈"]},
    "공기청정기": {"삼성": ["삼성공기청정기","삼성 공기청정기","비스포크 공기청정기","비스포크공기청정기"],
                  "LG":  ["LG공기청정기","LG 공기청정기","LG 퓨리케어 공기청정기","퓨리케어 공기청정기"]},
    "식기세척기": {"삼성": ["삼성식기세척기","삼성 식기세척기","비스포크식기세척기","비스포크 식기세척기"],
                  "LG":  ["LG식기세척기","LG 식기세척기","LG디오스식기세척기","LG 디오스 식기세척기"]},
    "청소기":    {"삼성": ["삼성청소기","삼성 청소기","비스포크제트","비스포크 제트","삼성 제트"],
                  "LG":  ["LG청소기","LG 청소기","코드제로","LG코드제로","LG 코드제로"]},
    "로봇청소기": {"삼성": ["삼성 로봇청소기","비스포크 로봇청소기","삼성 로봇청소기 추천"],
                  "LG":  ["LG 로봇청소기","코드제로 로봇청소기","LG 로봇청소기 추천"]},
    "의류관리기": {"삼성": ["에어드레서","삼성에어드레서","삼성 에어드레서","비스포크 에어드레서"],
                  "LG":  ["LG스타일러","LG 스타일러","스타일러","LG 의류관리기"]},
}

SUBSCRIBE_KEYWORDS = {
    "구독브랜드":    {"삼성": ["삼성구독","삼성 가전 구독","비스포크 구독","삼성 렌탈"],
                    "LG":   ["LG케어솔루션","케어솔루션","LG 구독","LG 렌탈"],
                    "코웨이":["코웨이","코웨이 렌탈","코웨이 구독"]},
    "정수기구독":    {"삼성": ["삼성 정수기 렌탈","비스포크 정수기 렌탈","삼성 정수기 구독"],
                    "LG":   ["LG 정수기 렌탈","퓨리케어 렌탈","LG 정수기 구독"],
                    "코웨이":["코웨이 정수기","코웨이 정수기 렌탈"]},
    "공기청정기구독": {"삼성": ["삼성 공기청정기 렌탈","비스포크 공기청정기 렌탈"],
                    "LG":   ["LG 공기청정기 렌탈","퓨리케어 공기청정기 렌탈"],
                    "코웨이":["코웨이 공기청정기","코웨이 공기청정기 렌탈"]},
    "에어컨구독":    {"삼성": ["삼성 에어컨 렌탈","무풍에어컨 렌탈","비스포크 에어컨 렌탈"],
                    "LG":   ["LG 에어컨 렌탈","휘센 에어컨 렌탈"]},
    "건조기구독":    {"삼성": ["삼성 건조기 렌탈","비스포크 건조기 렌탈"],
                    "LG":   ["LG 건조기 렌탈","트롬 건조기 렌탈"]},
    "세탁기구독":    {"삼성": ["삼성 세탁기 렌탈","비스포크 세탁기 렌탈"],
                    "LG":   ["LG 세탁기 렌탈","트롬 세탁기 렌탈"]},
    "식기세척기구독": {"삼성": ["삼성 식기세척기 렌탈","비스포크 식기세척기 렌탈"],
                    "LG":   ["LG 식기세척기 렌탈","디오스 식기세척기 렌탈"]},
    "의류관리기구독": {"삼성": ["에어드레서 렌탈","삼성 에어드레서 렌탈"],
                    "LG":   ["스타일러 렌탈","LG 스타일러 렌탈"]},
    "청소기구독":    {"삼성": ["삼성 청소기 렌탈","비스포크 제트 렌탈"],
                    "LG":   ["LG 청소기 렌탈","코드제로 렌탈"]},
    "로봇청소기구독": {"삼성": ["삼성 로봇청소기 렌탈","비스포크 로봇청소기 렌탈"],
                    "LG":   ["LG 로봇청소기 렌탈","코드제로 로봇청소기 렌탈"]},
    "가전구독일반":   {"삼성": ["삼성 가전 구독","삼성 가전 렌탈","삼성 구독 가전"],
                    "LG":   ["LG 가전 구독","LG 가전 렌탈","LG 케어솔루션"]},
}

# ── 유틸 ───────────────────────────────────────────────────────────

def latest_csv(pattern):
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, pattern)))
    return files[-1] if files else None

def load_csv(path):
    data, periods = {}, []
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cat, brand = row["카테고리"], row["브랜드"]
            fields = [k for k in row if k not in ("카테고리","브랜드")]
            if not periods:
                periods = fields
            data.setdefault(cat, {})[brand] = {
                p: float(row[p]) if row[p] else 0.0 for p in fields
            }
    return data, periods

def month_label(p):
    try:
        return datetime.strptime(p, "%Y-%m-%d").strftime("%y.%m")
    except Exception:
        return p

def keyword_table_html(cat_name, keyword_dict):
    if not keyword_dict:
        return ""
    rows = ""
    for brand, kws in keyword_dict.items():
        color = BRAND_COLORS.get(brand, "#888")
        pills = "".join(
            '<span class="kw-pill" style="border-color:{c};color:{c}">{k}</span>'.format(c=color, k=k)
            for k in kws
        )
        rows += '<tr><td class="kw-brand" style="color:{c}">{b}</td><td>{p}</td></tr>'.format(
            c=color, b=brand, p=pills)
    return """
    <details class="kw-details">
      <summary>검색어 보기</summary>
      <table class="kw-table">{rows}</table>
    </details>""".format(rows=rows)

def build_cards_html(section_id, data, keyword_dict):
    """각 카테고리 카드 HTML (canvas + 키워드 표)"""
    cards = ""
    for i, (cat, brands) in enumerate(data.items()):
        canvas_id = "{}_{}".format(section_id, i)
        kw_html = keyword_table_html(cat, keyword_dict.get(cat, {}))
        cards += """
        <div class="card">
            <div class="card-title">{cat}</div>
            <div class="chart-wrap"><canvas id="{cid}"></canvas></div>
            <div class="card-footer" id="{cid}_footer"></div>
            {kw}
        </div>""".format(cat=cat, cid=canvas_id, kw=kw_html)
    return cards

def build_js_data(section_id, data, periods, keyword_dict):
    """차트 데이터를 JS 변수로 직렬화 (keyword_dict에 없는 브랜드 제외)"""
    cats = list(data.keys())
    series = {}
    brands_per_cat = {}
    for cat, brands in data.items():
        allowed = set(keyword_dict[cat].keys()) if cat in keyword_dict else set(brands.keys())
        series[cat] = {}
        brands_per_cat[cat] = []
        for brand, vals in brands.items():
            if brand not in allowed:
                continue
            series[cat][brand] = [round(vals.get(p, 0), 2) for p in periods]
            brands_per_cat[cat].append(brand)

    labels = [month_label(p) for p in periods]

    return """
    const {sid}Data = {{
        periods: {periods},
        labels:  {labels},
        cats:    {cats},
        series:  {series},
        brandsPerCat: {bpc},
        colors:  {colors}
    }};""".format(
        sid=section_id,
        periods=json.dumps(periods),
        labels=json.dumps(labels),
        cats=json.dumps(cats),
        series=json.dumps(series, ensure_ascii=False),
        bpc=json.dumps(brands_per_cat, ensure_ascii=False),
        colors=json.dumps(BRAND_COLORS, ensure_ascii=False),
    )

# ── 이벤트 로드 / JS 직렬화 ────────────────────────────────────────

def load_events():
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "events_*.json")))
    if not files:
        return {}, {}
    with open(files[-1], encoding="utf-8") as f:
        d = json.load(f)
    return d.get("trend", {}), d.get("subscribe", {})


def build_js_events(trend_ev, subscribe_ev):
    """period 키 '2025-07-01' → label 키 '25.07' 로 변환해 JS 변수로 직렬화"""
    def convert(src):
        out = {}
        for cat, brands in src.items():
            out[cat] = {}
            for brand, pnews in brands.items():
                out[cat][brand] = {}
                for period, news in pnews.items():
                    out[cat][brand][month_label(period)] = {
                        "title":   news["title"],
                        "link":    news["link"],
                        "pubDate": news.get("pubDate", ""),
                    }
        return out

    return "\n    const trendEvents = {t};\n    const subscribeEvents = {s};".format(
        t=json.dumps(convert(trend_ev),     ensure_ascii=False),
        s=json.dumps(convert(subscribe_ev), ensure_ascii=False),
    )


# ── 메인 ───────────────────────────────────────────────────────────

def main():
    today_str = datetime.today().strftime("%Y%m%d")
    out_path  = os.path.join(OUTPUT_DIR, "monthly_charts_{}.html".format(today_str))

    trend_path     = latest_csv("trend_detail_*.csv")
    subscribe_path = latest_csv("subscribe_detail_*.csv")
    if not trend_path or not subscribe_path:
        print("CSV 파일 없음. 먼저 두 스크립트를 실행하세요.")
        return

    trend_data,     periods = load_csv(trend_path)
    subscribe_data, _       = load_csv(subscribe_path)

    print("  로드: {}, {}".format(os.path.basename(trend_path), os.path.basename(subscribe_path)))
    print("  기간: {} ~ {}  ({} 개월)".format(month_label(periods[0]), month_label(periods[-1]), len(periods)))

    cards_trend     = build_cards_html("trend",     trend_data,     TREND_KEYWORDS)
    cards_subscribe = build_cards_html("subscribe", subscribe_data, SUBSCRIBE_KEYWORDS)

    js_trend     = build_js_data("trend",     trend_data,     periods, TREND_KEYWORDS)
    js_subscribe = build_js_data("subscribe", subscribe_data, periods, SUBSCRIBE_KEYWORDS)

    trend_ev, subscribe_ev = load_events()
    js_events = build_js_events(trend_ev, subscribe_ev)
    n_events  = sum(len(p) for b in trend_ev.values() for p in b.values()) \
              + sum(len(p) for b in subscribe_ev.values() for p in b.values())
    print("  이벤트: {}건 로드".format(n_events))

    start_lbl = month_label(periods[0])
    end_lbl   = month_label(periods[-1])

    html = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>네이버 월별 검색량 비교 {date}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3"></script>
<script src="https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js"></script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,'Malgun Gothic',sans-serif;background:#f2f4f8;color:#222;padding-bottom:60px}}
/* header */
header{{background:linear-gradient(135deg,#0f1e6e 0%,#1428A0 60%,#3a5bd6 100%);color:#fff;padding:32px 40px 26px}}
header h1{{font-size:22px;font-weight:700;letter-spacing:-.5px}}
header p{{font-size:12px;opacity:.8;margin-top:5px}}
.legend-pills{{display:flex;gap:10px;margin-top:12px;flex-wrap:wrap}}
.pill{{display:flex;align-items:center;gap:6px;background:rgba(255,255,255,.15);border-radius:20px;padding:4px 12px;font-size:12px}}
.pill-dot{{width:9px;height:9px;border-radius:50%}}
/* section */
section{{max-width:1400px;margin:28px auto 0;padding:0 20px}}
.section-header{{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px}}
.section-title{{font-size:16px;font-weight:700;color:#1428A0;border-left:4px solid #1428A0;padding-left:11px}}
.section-controls{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
/* filter buttons */
.filter-group{{display:flex;gap:4px}}
.filter-btn{{
    font-size:12px;padding:5px 13px;border-radius:20px;border:1.5px solid #1428A0;
    background:#fff;color:#1428A0;cursor:pointer;font-weight:600;transition:all .15s
}}
.filter-btn:hover{{background:#eef1fb}}
.filter-btn.active{{background:#1428A0;color:#fff}}
/* excel button */
.excel-btn{{
    font-size:12px;padding:5px 14px;border-radius:20px;border:none;
    background:#217346;color:#fff;cursor:pointer;font-weight:600;
    display:flex;align-items:center;gap:5px;transition:opacity .15s
}}
.excel-btn:hover{{opacity:.85}}
.excel-btn svg{{width:13px;height:13px}}
/* summary bar */
.summary-wrap{{background:#fff;border-radius:14px;padding:18px 22px;margin-bottom:22px;box-shadow:0 2px 10px rgba(0,0,0,.07)}}
.summary-wrap h3{{font-size:13px;color:#666;margin-bottom:12px}}
.summary-bar-wrap{{height:190px}}
/* grid */
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:14px}}
.card{{background:#fff;border-radius:14px;padding:18px 18px 12px;box-shadow:0 2px 10px rgba(0,0,0,.07);transition:box-shadow .2s}}
.card:hover{{box-shadow:0 6px 20px rgba(0,0,0,.12)}}
.card-title{{font-size:14px;font-weight:700;color:#222;margin-bottom:10px}}
.chart-wrap{{height:175px;position:relative}}
.card-footer{{font-size:11.5px;color:#555;margin-top:8px;text-align:center;min-height:18px}}
/* keywords */
.kw-details{{margin-top:8px;border-top:1px solid #eee;padding-top:7px}}
.kw-details summary{{font-size:11px;color:#999;cursor:pointer;user-select:none;list-style:none;display:flex;align-items:center;gap:4px}}
.kw-details summary::before{{content:'▶';font-size:8px;transition:transform .2s;display:inline-block}}
.kw-details[open] summary::before{{transform:rotate(90deg)}}
.kw-details summary:hover{{color:#555}}
.kw-table{{width:100%;border-collapse:collapse;margin-top:6px;font-size:11px}}
.kw-table tr{{vertical-align:top}}
.kw-table td{{padding:2px 4px}}
.kw-brand{{font-weight:700;white-space:nowrap;padding-right:8px!important;width:44px}}
.kw-pill{{display:inline-block;border:1px solid;border-radius:10px;padding:1px 7px;margin:2px 2px;font-size:10px;background:#fafafa}}
hr.divider{{border:none;border-top:1px solid #ddd;margin:32px 0 0}}
/* 뉴스 툴팁 */
#news-tt{{
    display:none;position:fixed;z-index:9999;pointer-events:none;
    background:#fff;border-radius:10px;padding:11px 14px;max-width:280px;
    box-shadow:0 4px 20px rgba(0,0,0,.18);border:1px solid #eee;
}}
#news-tt .nt-brand{{font-size:11px;font-weight:700;margin-bottom:3px}}
#news-tt .nt-date{{font-size:10px;color:#aaa;margin-bottom:6px}}
#news-tt .nt-title{{font-size:12px;color:#222;line-height:1.5}}
#news-tt .nt-hint{{font-size:10px;color:#888;margin-top:7px}}
</style>
</head>
<body>
<div id="news-tt">
  <div class="nt-brand" id="nt-brand"></div>
  <div class="nt-date"  id="nt-date"></div>
  <div class="nt-title" id="nt-title"></div>
  <div class="nt-hint">클릭하여 기사 보기 →</div>
</div>
<header>
  <h1>📊 네이버 월별 검색량 비교 차트</h1>
  <p>기간: {start} ~ {end} &nbsp;|&nbsp; 단위: 월간 상대지수 &nbsp;|&nbsp; 생성일: {date}</p>
  <div class="legend-pills">
    <div class="pill"><div class="pill-dot" style="background:#1428A0"></div>삼성</div>
    <div class="pill"><div class="pill-dot" style="background:#A50034"></div>LG</div>
    <div class="pill"><div class="pill-dot" style="background:#00A651"></div>코웨이 (구독 일부)</div>
  </div>
</header>

<!-- ── 구독/렌탈 ──────────────────────────────────────────────── -->
<section>
  <div class="section-header">
    <span class="section-title">구독 / 렌탈 — 삼성 vs LG vs 코웨이</span>
    <div class="section-controls">
      <div class="filter-group" id="subscribe-filter">
        <button class="filter-btn active" onclick="filterSection('subscribe',13,this)">최근 1년</button>
        <button class="filter-btn"        onclick="filterSection('subscribe',6,this)">최근 6개월</button>
        <button class="filter-btn"        onclick="filterSection('subscribe',3,this)">최근 3개월</button>
      </div>
      <button class="excel-btn" onclick="downloadExcel('subscribe')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/><line x1="9" y1="11" x2="15" y2="11"/></svg>
        엑셀 다운로드
      </button>
    </div>
  </div>
  <div class="summary-wrap">
    <h3>카테고리별 평균 점수</h3>
    <div class="summary-bar-wrap"><canvas id="subscribe_bar"></canvas></div>
  </div>
  <div class="grid" id="subscribe-grid">{cards_subscribe}
  </div>
</section>

<hr class="divider">

<!-- ── 일반 가전 ─────────────────────────────────────────────── -->
<section style="margin-top:28px">
  <div class="section-header">
    <span class="section-title">일반 가전 — 삼성 vs LG</span>
    <div class="section-controls">
      <div class="filter-group" id="trend-filter">
        <button class="filter-btn active" onclick="filterSection('trend',13,this)">최근 1년</button>
        <button class="filter-btn"        onclick="filterSection('trend',6,this)">최근 6개월</button>
        <button class="filter-btn"        onclick="filterSection('trend',3,this)">최근 3개월</button>
      </div>
      <button class="excel-btn" onclick="downloadExcel('trend')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/><line x1="9" y1="11" x2="15" y2="11"/></svg>
        엑셀 다운로드
      </button>
    </div>
  </div>
  <div class="summary-wrap">
    <h3>카테고리별 평균 점수</h3>
    <div class="summary-bar-wrap"><canvas id="trend_bar"></canvas></div>
  </div>
  <div class="grid" id="trend-grid">{cards_trend}
  </div>
</section>

<script>
{js_trend}
{js_subscribe}
{js_events}

// ── 뉴스 툴팁 ────────────────────────────────────────
let _mouseX = 0, _mouseY = 0;
document.addEventListener('mousemove', e => {{ _mouseX = e.clientX; _mouseY = e.clientY; }});

function showNewsTooltip(brand, info, event) {{
    const tt = document.getElementById('news-tt');
    const COLORS = {{"삼성":"#1428A0","LG":"#A50034","코웨이":"#00A651"}};
    document.getElementById('nt-brand').style.color = COLORS[brand] || '#333';
    document.getElementById('nt-brand').textContent = brand;
    document.getElementById('nt-date').textContent  = info.pubDate;
    document.getElementById('nt-title').textContent = info.title;
    tt._link = info.link;
    const x = (event && event.native) ? event.native.clientX : _mouseX;
    const y = (event && event.native) ? event.native.clientY : _mouseY;
    tt.style.left    = (x + 14) + 'px';
    tt.style.top     = (y - 20) + 'px';
    tt.style.display = 'block';
}}
function hideNewsTooltip() {{
    document.getElementById('news-tt').style.display = 'none';
}}
document.getElementById('news-tt').addEventListener('click', () => {{
    const link = document.getElementById('news-tt')._link;
    if (link) window.open(link, '_blank');
}});
document.getElementById('news-tt').style.pointerEvents = 'auto';
document.getElementById('news-tt').style.cursor = 'pointer';

// ── 뉴스 annotation 생성 ─────────────────────────────
function buildNewsAnnotations(sid, cat, labels, series) {{
    const evSrc = sid === 'trend' ? trendEvents : subscribeEvents;
    if (!evSrc || !evSrc[cat]) return {{}};
    const out = {{}};
    let idx = 0;
    for (const brand of Object.keys(evSrc[cat])) {{
        for (const period of Object.keys(evSrc[cat][brand])) {{
            const li = labels.indexOf(period);
            if (li < 0) continue;
            const info       = evSrc[cat][brand][period];
            const brandSer   = series[cat] && series[cat][brand];
            const yVal       = brandSer ? brandSer[li] : null;
            const key        = 'news_' + brand + '_' + idx;
            const _brand     = brand;
            const _info      = info;
            out[key] = {{
                type: 'label',
                xValue: period,
                yValue: yVal,
                yAdjust: -22,
                content: '⭐',
                font: {{ size: 15 }},
                backgroundColor: 'transparent',
                borderWidth: 0,
                padding: 0,
                enter(ctx, evt) {{ showNewsTooltip(_brand, _info, evt); }},
                leave()         {{ hideNewsTooltip(); }},
                click(ctx, evt) {{ window.open(_info.link, '_blank'); }}
            }};
            idx++;
        }}
    }}
    return out;
}}

// ── 차트 인스턴스 저장소 ─────────────────────────────
const chartInstances = {{ trend: {{}}, subscribe: {{}} }};
const barInstances   = {{ trend: null, subscribe: null }};

// ── 유틸: 라벨 단축 ─────────────────────────────────
function ml(p) {{
    const d = new Date(p);
    return (d.getFullYear()%100).toString().padStart(2,'0') + '.' + (d.getMonth()+1).toString().padStart(2,'0');
}}

// ── 슬라이스된 데이터 반환 ───────────────────────────
function slicedData(sectionData, months) {{
    const n = Math.min(months, sectionData.periods.length);
    const pSlice = sectionData.periods.slice(-n);
    const lSlice = sectionData.labels.slice(-n);
    const seriesSlice = {{}};
    for (const cat of sectionData.cats) {{
        seriesSlice[cat] = {{}};
        for (const brand of sectionData.brandsPerCat[cat]) {{
            seriesSlice[cat][brand] = sectionData.series[cat][brand].slice(-n);
        }}
    }}
    return {{ periods: pSlice, labels: lSlice, series: seriesSlice }};
}}

// ── 갭 annotation 생성 ───────────────────────────────
function buildGapAnnotations(cat, seriesSlice, labels, filterLabel) {{
    const s = seriesSlice[cat] && seriesSlice[cat]['삼성'];
    const l = seriesSlice[cat] && seriesSlice[cat]['LG'];
    if (!s || !l || s.length === 0) return {{}};

    function calcGap(sv, lv) {{ return lv !== 0 ? (sv - lv) / lv * 100 : 0; }}

    function anno(xLabel, sv, lv, extraLine) {{
        const gap   = calcGap(sv, lv);
        const color = gap >= 0 ? '#1428A0' : '#A50034';
        const sign  = gap >= 0 ? '+' : '';
        const lines = [`${{sign}}${{gap.toFixed(1)}}%`];
        if (extraLine) lines.push(extraLine);
        return {{
            type: 'line',
            xMin: xLabel, xMax: xLabel,
            yMin: Math.min(sv, lv), yMax: Math.max(sv, lv),
            borderColor: color, borderWidth: 2,
            arrowHeads: {{
                start: {{ enabled: true, fill: true, width: 7, length: 7 }},
                end:   {{ enabled: true, fill: true, width: 7, length: 7 }}
            }},
            label: {{
                display: true,
                content: lines.length === 1 ? lines[0] : lines,
                backgroundColor: color + 'ee',
                color: '#fff',
                font: {{ size: 11, weight: 'bold' }},
                padding: {{ x: 5, y: 3 }},
                borderRadius: 4,
                position: '50%'
            }}
        }};
    }}

    const n = s.length;

    // 가장 최근 월 annotation: 현재갭 + 기간比 변화량
    let deltaLine = null;
    if (n > 1 && filterLabel) {{
        const delta = calcGap(s[n-1], l[n-1]) - calcGap(s[0], l[0]);
        const tri   = delta >= 0 ? '🔺' : '🔻';
        deltaLine   = `${{filterLabel}}比 ${{tri}}${{Math.abs(delta).toFixed(1)}}%p`;
    }}

    const out = {{ gapEnd: anno(labels[n-1], s[n-1], l[n-1], deltaLine) }};
    if (n > 1) out.gapStart = anno(labels[0], s[0], l[0], null);
    return out;
}}

// ── footer 텍스트 업데이트 ────────────────────────────
function updateFooter(cid, cat, seriesSlice, brandsPerCat, labels) {{
    const brands = brandsPerCat[cat];
    const avgs = {{}};
    brands.forEach(b => {{
        const vals = seriesSlice[cat][b];
        avgs[b] = vals.reduce((a,v)=>a+v,0) / (vals.length||1);
    }});
    const winner = brands.reduce((a,b)=>avgs[a]>=avgs[b]?a:b);
    const COLORS = {{"삼성":"#1428A0","LG":"#A50034","코웨이":"#00A651"}};
    const parts = brands.map(b=>`<span style="color:${{COLORS[b]||'#333'}}">${{b}} ${{avgs[b].toFixed(1)}}</span>`);
    const wc = COLORS[winner]||'#333';
    document.getElementById(cid+'_footer').innerHTML =
        parts.join('  |  ') + `&nbsp;→&nbsp;<strong style="color:${{wc}}">${{winner}} 우세</strong>`;
}}

// ── 바차트 업데이트 ──────────────────────────────────
function updateBarChart(sid, sectionData, seriesSlice) {{
    const cats   = sectionData.cats;
    const allBrands = [...new Set(cats.flatMap(c=>sectionData.brandsPerCat[c]))];
    const COLORS = {{"삼성":"#1428A0CC","LG":"#A50034CC","코웨이":"#00A651CC"}};
    const datasets = allBrands.map(b=>{{
        const vals = cats.map(cat=>{{
            const s = seriesSlice.series[cat][b];
            return s ? parseFloat((s.reduce((a,v)=>a+v,0)/(s.length||1)).toFixed(1)) : 0;
        }});
        return {{ label:b, data:vals, backgroundColor:COLORS[b]||'#88888888', borderRadius:4 }};
    }});
    const bar = barInstances[sid];
    bar.data.labels   = cats;
    bar.data.datasets = datasets;
    bar.update();
}}

// ── 섹션 초기 빌드 ────────────────────────────────────
const FILTER_LABELS = {{ 13: '1년전', 6: '6개월전', 3: '3개월전' }};

function buildSection(sid, sectionData, months) {{
    const {{ periods, labels, series }} = slicedData(sectionData, months);
    const cats = sectionData.cats;
    const filterLabel = FILTER_LABELS[months] || '1년전';
    const COLORS = {{"삼성":"#1428A0","LG":"#A50034","코웨이":"#00A651"}};

    cats.forEach((cat, i) => {{
        const cid = sid+'_'+i;
        const brands = sectionData.brandsPerCat[cat];
        const datasets = brands.map(b=>{{
            const c = COLORS[b]||'#888';
            return {{
                label: b,
                data: series[cat][b],
                borderColor: c,
                backgroundColor: c+'18',
                borderWidth: 2.5,
                pointRadius: 3,
                tension: 0.35,
                fill: false
            }};
        }});
        const ctx = document.getElementById(cid);
        if (!ctx) return;
        chartInstances[sid][cat] = new Chart(ctx, {{
            type: 'line',
            data: {{ labels, datasets }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode:'index', intersect:false }},
                plugins: {{
                    legend: {{ position:'top', labels:{{ font:{{size:11}}, padding:10 }} }},
                    tooltip: {{ callbacks: {{ label: ctx=>`  ${{ctx.dataset.label}}: ${{ctx.parsed.y.toFixed(1)}}` }} }},
                    annotation: {{ annotations: Object.assign({{}}, buildGapAnnotations(cat, series, labels, filterLabel), buildNewsAnnotations(sid, cat, labels, series)) }}
                }},
                scales: {{
                    x: {{ grid:{{display:false}}, ticks:{{font:{{size:10}}}} }},
                    y: {{ beginAtZero:true, grid:{{color:'#f0f0f0'}}, ticks:{{font:{{size:10}}}} }}
                }}
            }}
        }});
        updateFooter(cid, cat, series, sectionData.brandsPerCat, labels);
    }});

    // 바 차트
    const allBrands = [...new Set(cats.flatMap(c=>sectionData.brandsPerCat[c]))];
    const COLORSCC  = {{"삼성":"#1428A0CC","LG":"#A50034CC","코웨이":"#00A651CC"}};
    const barDatasets = allBrands.map(b=>{{
        const vals = cats.map(cat=>{{
            const s = series[cat][b];
            return s ? parseFloat((s.reduce((a,v)=>a+v,0)/(s.length||1)).toFixed(1)) : 0;
        }});
        return {{ label:b, data:vals, backgroundColor:COLORSCC[b]||'#88888888', borderRadius:4 }};
    }});
    barInstances[sid] = new Chart(document.getElementById(sid+'_bar'), {{
        type: 'bar',
        data: {{ labels: cats, datasets: barDatasets }},
        options: {{
            responsive:true, maintainAspectRatio:false,
            plugins:{{ legend:{{ position:'top' }} }},
            scales:{{
                y:{{ beginAtZero:true, grid:{{color:'#f0f0f0'}} }},
                x:{{ grid:{{display:false}} }}
            }}
        }}
    }});
}}

// ── 타임라인 필터 ────────────────────────────────────
function filterSection(sid, months, btn) {{
    // 버튼 active 표시
    document.querySelectorAll('#'+sid+'-filter .filter-btn').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');

    const sectionData = sid==='trend' ? trendData : subscribeData;
    const {{ periods, labels, series }} = slicedData(sectionData, months);
    const filterLabel = FILTER_LABELS[months] || '';

    sectionData.cats.forEach((cat, i) => {{
        const cid = sid+'_'+i;
        const chart = chartInstances[sid][cat];
        if (!chart) return;
        const brands = sectionData.brandsPerCat[cat];
        chart.data.labels = labels;
        brands.forEach((b, di) => {{
            chart.data.datasets[di].data = series[cat][b];
        }});
        chart.options.plugins.annotation.annotations = Object.assign({{}}, buildGapAnnotations(cat, series, labels, filterLabel), buildNewsAnnotations(sid, cat, labels, series));
        chart.update();
        updateFooter(cid, cat, series, sectionData.brandsPerCat, labels);
    }});
    updateBarChart(sid, sectionData, {{ series }});
}}

// ── 엑셀 다운로드 ────────────────────────────────────
function downloadExcel(sid) {{
    const sectionData = sid==='trend' ? trendData : subscribeData;
    const wb = XLSX.utils.book_new();
    const periods = sectionData.periods;

    // 전체 요약 시트
    const summaryRows = [['카테고리','브랜드',...periods.map(ml)]];
    sectionData.cats.forEach(cat=>{{
        sectionData.brandsPerCat[cat].forEach(b=>{{
            summaryRows.push([cat, b, ...sectionData.series[cat][b]]);
        }});
    }});
    XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(summaryRows), '전체');

    // 카테고리별 시트
    sectionData.cats.forEach(cat=>{{
        const rows = [['월', ...sectionData.brandsPerCat[cat]]];
        periods.forEach((p, pi)=>{{
            rows.push([ml(p), ...sectionData.brandsPerCat[cat].map(b=>sectionData.series[cat][b][pi])]);
        }});
        XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(rows), cat.slice(0,31));
    }});

    const filename = sid==='trend'
        ? '일반가전_트렌드_{date}.xlsx'
        : '구독렌탈_트렌드_{date}.xlsx';
    XLSX.writeFile(wb, filename);
}}

// ── 초기 렌더 ────────────────────────────────────────
buildSection('trend',     trendData,     13);
buildSection('subscribe', subscribeData, 13);
</script>
</body>
</html>""".format(
        date=today_str,
        start=start_lbl,
        end=end_lbl,
        cards_trend=cards_trend,
        cards_subscribe=cards_subscribe,
        js_trend=js_trend,
        js_subscribe=js_subscribe,
        js_events=js_events,
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("\n  ✔ 저장 완료: {}".format(out_path))
    return out_path

if __name__ == "__main__":
    main()
