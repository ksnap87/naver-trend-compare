#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 CSV 데이터로 월별 검색량 비교 차트 HTML 생성
각 카테고리 카드에 사용 키워드 표 포함
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

BRAND_COLORS = {
    "삼성":  SAMSUNG_COLOR,
    "LG":    LG_COLOR,
    "코웨이": COWAY_COLOR,
}

# ── 카테고리별 사용 키워드 정의 ────────────────────────────────────

TREND_KEYWORDS = {
    "냉장고": {
        "삼성": ["삼성냉장고", "삼성 냉장고", "비스포크냉장고", "비스포크 냉장고", "삼성 냉장고 추천"],
        "LG":   ["LG냉장고", "LG 냉장고", "오브제냉장고", "LG 오브제 냉장고", "LG 냉장고 추천"],
    },
    "세탁기": {
        "삼성": ["삼성세탁기", "삼성 세탁기", "비스포크세탁기", "비스포크 세탁기", "삼성 그랑데"],
        "LG":   ["LG세탁기", "LG 세탁기", "LG트롬", "LG 트롬 세탁기", "트롬세탁기"],
    },
    "에어컨": {
        "삼성": ["삼성에어컨", "삼성 에어컨", "무풍에어컨", "비스포크에어컨", "비스포크 에어컨"],
        "LG":   ["LG에어컨", "LG 에어컨", "휘센에어컨", "LG휘센", "LG 휘센 에어컨"],
    },
    "TV": {
        "삼성": ["삼성TV", "삼성 TV", "네오QLED", "삼성 네오QLED", "삼성 QLED"],
        "LG":   ["LGTV", "LG TV", "LG OLED", "LG 올레드", "LG OLED TV"],
    },
    "건조기": {
        "삼성": ["삼성건조기", "삼성 건조기", "비스포크건조기", "비스포크 건조기", "삼성 그랑데 건조기"],
        "LG":   ["LG건조기", "LG 건조기", "LG트롬건조기", "LG 트롬 건조기", "트롬건조기"],
    },
    "정수기": {
        "삼성": ["삼성정수기", "삼성 정수기", "비스포크정수기", "비스포크 정수기", "삼성 정수기 렌탈"],
        "LG":   ["LG정수기", "LG 정수기", "퓨리케어정수기", "LG 퓨리케어", "LG 정수기 렌탈"],
    },
    "공기청정기": {
        "삼성": ["삼성공기청정기", "삼성 공기청정기", "비스포크 공기청정기", "비스포크공기청정기"],
        "LG":   ["LG공기청정기", "LG 공기청정기", "LG 퓨리케어 공기청정기", "퓨리케어 공기청정기"],
    },
    "식기세척기": {
        "삼성": ["삼성식기세척기", "삼성 식기세척기", "비스포크식기세척기", "비스포크 식기세척기"],
        "LG":   ["LG식기세척기", "LG 식기세척기", "LG디오스식기세척기", "LG 디오스 식기세척기"],
    },
    "청소기": {
        "삼성": ["삼성청소기", "삼성 청소기", "비스포크제트", "비스포크 제트", "삼성 제트"],
        "LG":   ["LG청소기", "LG 청소기", "코드제로", "LG코드제로", "LG 코드제로"],
    },
    "로봇청소기": {
        "삼성": ["삼성 로봇청소기", "비스포크 로봇청소기", "삼성 로봇청소기 추천"],
        "LG":   ["LG 로봇청소기", "코드제로 로봇청소기", "LG 로봇청소기 추천"],
    },
    "의류관리기": {
        "삼성": ["에어드레서", "삼성에어드레서", "삼성 에어드레서", "비스포크 에어드레서"],
        "LG":   ["LG스타일러", "LG 스타일러", "스타일러", "LG 의류관리기"],
    },
}

SUBSCRIBE_KEYWORDS = {
    "구독브랜드": {
        "삼성":  ["삼성구독", "삼성 가전 구독", "비스포크 구독", "삼성 렌탈"],
        "LG":    ["LG케어솔루션", "케어솔루션", "LG 구독", "LG 렌탈"],
        "코웨이": ["코웨이", "코웨이 렌탈", "코웨이 구독"],
    },
    "정수기구독": {
        "삼성":  ["삼성 정수기 렌탈", "비스포크 정수기 렌탈", "삼성 정수기 구독"],
        "LG":    ["LG 정수기 렌탈", "퓨리케어 렌탈", "LG 정수기 구독"],
        "코웨이": ["코웨이 정수기", "코웨이 정수기 렌탈"],
    },
    "공기청정기구독": {
        "삼성":  ["삼성 공기청정기 렌탈", "비스포크 공기청정기 렌탈"],
        "LG":    ["LG 공기청정기 렌탈", "퓨리케어 공기청정기 렌탈"],
        "코웨이": ["코웨이 공기청정기", "코웨이 공기청정기 렌탈"],
    },
    "에어컨구독": {
        "삼성": ["삼성 에어컨 렌탈", "무풍에어컨 렌탈", "비스포크 에어컨 렌탈"],
        "LG":   ["LG 에어컨 렌탈", "휘센 에어컨 렌탈"],
    },
    "건조기구독": {
        "삼성": ["삼성 건조기 렌탈", "비스포크 건조기 렌탈"],
        "LG":   ["LG 건조기 렌탈", "트롬 건조기 렌탈"],
    },
    "세탁기구독": {
        "삼성": ["삼성 세탁기 렌탈", "비스포크 세탁기 렌탈"],
        "LG":   ["LG 세탁기 렌탈", "트롬 세탁기 렌탈"],
    },
    "식기세척기구독": {
        "삼성": ["삼성 식기세척기 렌탈", "비스포크 식기세척기 렌탈"],
        "LG":   ["LG 식기세척기 렌탈", "디오스 식기세척기 렌탈"],
    },
    "의류관리기구독": {
        "삼성": ["에어드레서 렌탈", "삼성 에어드레서 렌탈"],
        "LG":   ["스타일러 렌탈", "LG 스타일러 렌탈"],
    },
    "청소기구독": {
        "삼성": ["삼성 청소기 렌탈", "비스포크 제트 렌탈"],
        "LG":   ["LG 청소기 렌탈", "코드제로 렌탈"],
    },
    "로봇청소기구독": {
        "삼성": ["삼성 로봇청소기 렌탈", "비스포크 로봇청소기 렌탈"],
        "LG":   ["LG 로봇청소기 렌탈", "코드제로 로봇청소기 렌탈"],
    },
    "가전구독일반": {
        "삼성":  ["삼성 가전 구독", "삼성 가전 렌탈", "삼성 구독 가전"],
        "LG":    ["LG 가전 구독", "LG 가전 렌탈", "LG 케어솔루션"],
        "코웨이": ["코웨이 렌탈 추천", "코웨이 가격", "코웨이 렌탈 가격"],
    },
}


def latest_csv(pattern):
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, pattern)))
    return files[-1] if files else None


def load_csv(path):
    data = {}
    periods = []
    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat    = row["카테고리"]
            brand  = row["브랜드"]
            fields = [k for k in row.keys() if k not in ("카테고리", "브랜드")]
            if not periods:
                periods = fields
            if cat not in data:
                data[cat] = {}
            data[cat][brand] = {p: float(row[p]) if row[p] else 0.0 for p in fields}
    return data, periods


def month_label(period_str):
    try:
        from datetime import datetime as dt
        d = dt.strptime(period_str, "%Y-%m-%d")
        return d.strftime("%y.%m")
    except Exception:
        return period_str


def keyword_table_html(cat_name, keyword_dict):
    """카테고리 키워드를 브랜드별 표로 렌더링"""
    if not keyword_dict:
        return ""
    rows = ""
    for brand, kws in keyword_dict.items():
        color = BRAND_COLORS.get(brand, "#888")
        pills = "".join(f'<span class="kw-pill" style="border-color:{color};color:{color}">{k}</span>' for k in kws)
        rows += f'<tr><td class="kw-brand" style="color:{color}">{brand}</td><td>{pills}</td></tr>'
    return f"""
    <details class="kw-details">
      <summary>검색어 보기</summary>
      <table class="kw-table">{rows}</table>
    </details>"""


def make_line_chart(canvas_id, periods, brands_data):
    labels = json.dumps([month_label(p) for p in periods])
    datasets = []
    for brand, values in brands_data.items():
        color = BRAND_COLORS.get(brand, "#888888")
        data_vals = json.dumps([round(values.get(p, 0), 1) for p in periods])
        datasets.append(f"""{{
                label: '{brand}',
                data: {data_vals},
                borderColor: '{color}',
                backgroundColor: '{color}18',
                borderWidth: 2.5,
                pointRadius: 3,
                tension: 0.35,
                fill: false
            }}""")
    datasets_js = ",\n            ".join(datasets)
    return f"""
        new Chart(document.getElementById('{canvas_id}'), {{
            type: 'line',
            data: {{
                labels: {labels},
                datasets: [
                    {datasets_js}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                interaction: {{ mode: 'index', intersect: false }},
                plugins: {{
                    legend: {{ position: 'top', labels: {{ font: {{ size: 12 }}, padding: 12 }} }},
                    tooltip: {{ callbacks: {{ label: ctx => ` ${{ctx.dataset.label}}: ${{ctx.parsed.y.toFixed(1)}}` }} }}
                }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 11 }} }} }},
                    y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }}, ticks: {{ font: {{ size: 11 }} }} }}
                }}
            }}
        }});"""


def build_section(section_id, data, periods, keyword_dict):
    cards_html = ""
    charts_js  = []
    for i, (cat, brands) in enumerate(data.items()):
        canvas_id = f"{section_id}_{i}"
        avgs   = {b: sum(v.values()) / len(v) for b, v in brands.items() if v}
        winner = max(avgs, key=avgs.get) if avgs else "—"
        wcolor = BRAND_COLORS.get(winner, "#333")
        avg_strs = "  |  ".join(
            "<span style='color:{}'>{} {:.1f}</span>".format(BRAND_COLORS.get(b, "#333"), b, a)
            for b, a in avgs.items()
        )
        kw_html = keyword_table_html(cat, keyword_dict.get(cat, {}))

        cards_html += f"""
        <div class="card">
            <div class="card-title">{cat}</div>
            <div class="chart-wrap"><canvas id="{canvas_id}"></canvas></div>
            <div class="card-footer">{avg_strs} &nbsp;→&nbsp; <strong style="color:{wcolor}">{winner} 우세</strong></div>
            {kw_html}
        </div>"""
        charts_js.append(make_line_chart(canvas_id, periods, brands))

    return cards_html, charts_js


def main():
    today_str = datetime.today().strftime("%Y%m%d")
    out_path  = os.path.join(OUTPUT_DIR, f"monthly_charts_{today_str}.html")

    trend_path     = latest_csv("trend_detail_*.csv")
    subscribe_path = latest_csv("subscribe_detail_*.csv")

    if not trend_path or not subscribe_path:
        print("CSV 파일을 찾을 수 없습니다.")
        return

    trend_data,     periods1 = load_csv(trend_path)
    subscribe_data, periods2 = load_csv(subscribe_path)
    periods = periods1 or periods2

    print(f"  데이터 로드: {os.path.basename(trend_path)}, {os.path.basename(subscribe_path)}")
    print(f"  기간: {month_label(periods[0])} ~ {month_label(periods[-1])}  ({len(periods)}개월)")

    cards1, js1 = build_section("가전", trend_data,     periods, TREND_KEYWORDS)
    cards2, js2 = build_section("구독", subscribe_data, periods, SUBSCRIBE_KEYWORDS)

    all_js = "\n".join(js1 + js2)

    def bar_data(data_dict):
        cats, s_vals, l_vals, c_vals = [], [], [], []
        for cat, brands in data_dict.items():
            cats.append(cat)
            s_vals.append(round(sum(brands.get("삼성", {}).values()) / max(len(brands.get("삼성", {})), 1), 1))
            l_vals.append(round(sum(brands.get("LG",   {}).values()) / max(len(brands.get("LG",   {})), 1), 1))
            c = brands.get("코웨이", {})
            c_vals.append(round(sum(c.values()) / max(len(c), 1), 1) if c else 0)
        return cats, s_vals, l_vals, c_vals

    cats1, s1, l1, c1 = bar_data(trend_data)
    cats2, s2, l2, c2 = bar_data(subscribe_data)

    bar_js = f"""
        new Chart(document.getElementById('bar_trend'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(cats1)},
                datasets: [
                    {{ label: '삼성', data: {json.dumps(s1)}, backgroundColor: '{SAMSUNG_COLOR}CC', borderRadius: 4 }},
                    {{ label: 'LG',   data: {json.dumps(l1)}, backgroundColor: '{LG_COLOR}CC',      borderRadius: 4 }}
                ]
            }},
            options: {{ responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }}, x: {{ grid: {{ display: false }} }} }} }}
        }});
        new Chart(document.getElementById('bar_subscribe'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(cats2)},
                datasets: [
                    {{ label: '삼성',  data: {json.dumps(s2)}, backgroundColor: '{SAMSUNG_COLOR}CC', borderRadius: 4 }},
                    {{ label: 'LG',    data: {json.dumps(l2)}, backgroundColor: '{LG_COLOR}CC',      borderRadius: 4 }},
                    {{ label: '코웨이', data: {json.dumps(c2)}, backgroundColor: '{COWAY_COLOR}CC',   borderRadius: 4 }}
                ]
            }},
            options: {{ responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'top' }} }},
                scales: {{ y: {{ beginAtZero: true, grid: {{ color: '#f0f0f0' }} }}, x: {{ grid: {{ display: false }} }} }} }}
        }});"""

    start_lbl = month_label(periods[0])
    end_lbl   = month_label(periods[-1])

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>네이버 월별 검색량 비교 {today_str}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    font-family: -apple-system, 'Malgun Gothic', sans-serif;
    background: #f2f4f8;
    color: #222;
    padding: 0 0 60px;
}}
header {{
    background: linear-gradient(135deg, #0f1e6e 0%, #1428A0 60%, #3a5bd6 100%);
    color: #fff;
    padding: 36px 40px 28px;
}}
header h1 {{ font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
header p  {{ font-size: 13px; opacity: 0.8; margin-top: 6px; }}
.legend-pills {{ display: flex; gap: 12px; margin-top: 14px; flex-wrap: wrap; }}
.pill {{
    display: flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.15); border-radius: 20px;
    padding: 4px 12px; font-size: 13px;
}}
.pill-dot {{ width: 10px; height: 10px; border-radius: 50%; }}
section {{ max-width: 1400px; margin: 32px auto 0; padding: 0 20px; }}
.section-title {{
    font-size: 17px; font-weight: 700; color: #1428A0;
    border-left: 4px solid #1428A0; padding-left: 12px;
    margin-bottom: 18px;
}}
.summary-wrap {{
    background: #fff; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 28px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
}}
.summary-wrap h3 {{ font-size: 14px; color: #555; margin-bottom: 14px; }}
.summary-bar-wrap {{ height: 200px; }}
.grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
    gap: 16px;
}}
.card {{
    background: #fff;
    border-radius: 14px;
    padding: 20px 20px 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    transition: box-shadow 0.2s;
}}
.card:hover {{ box-shadow: 0 6px 20px rgba(0,0,0,0.12); }}
.card-title {{
    font-size: 15px; font-weight: 700; color: #222;
    margin-bottom: 12px; letter-spacing: -0.3px;
}}
.chart-wrap {{ height: 180px; position: relative; }}
.card-footer {{
    font-size: 12px; color: #555;
    margin-top: 10px; text-align: center;
    line-height: 1.6;
}}

/* 키워드 테이블 */
.kw-details {{
    margin-top: 10px;
    border-top: 1px solid #eee;
    padding-top: 8px;
}}
.kw-details summary {{
    font-size: 11px; color: #888; cursor: pointer;
    user-select: none; list-style: none;
    display: flex; align-items: center; gap: 4px;
}}
.kw-details summary::before {{
    content: '▶';
    font-size: 9px;
    transition: transform 0.2s;
    display: inline-block;
}}
.kw-details[open] summary::before {{ transform: rotate(90deg); }}
.kw-details summary:hover {{ color: #444; }}
.kw-table {{
    width: 100%; border-collapse: collapse;
    margin-top: 8px; font-size: 11px;
}}
.kw-table tr {{ vertical-align: top; }}
.kw-table td {{ padding: 3px 4px; }}
.kw-brand {{
    font-weight: 700; white-space: nowrap;
    padding-right: 8px !important; width: 44px;
}}
.kw-pill {{
    display: inline-block;
    border: 1px solid;
    border-radius: 10px;
    padding: 1px 7px;
    margin: 2px 2px;
    font-size: 10.5px;
    background: #fafafa;
}}
.divider {{ border: none; border-top: 1px solid #e0e0e0; margin: 36px 0 0; }}
</style>
</head>
<body>

<header>
  <h1>📊 네이버 월별 검색량 비교 차트</h1>
  <p>기간: {start_lbl} ~ {end_lbl} &nbsp;|&nbsp; 단위: 월간 상대지수 &nbsp;|&nbsp; 생성일: {today_str}</p>
  <div class="legend-pills">
    <div class="pill"><div class="pill-dot" style="background:#1428A0"></div>삼성</div>
    <div class="pill"><div class="pill-dot" style="background:#A50034"></div>LG</div>
    <div class="pill"><div class="pill-dot" style="background:#00A651"></div>코웨이 (구독 일부)</div>
  </div>
</header>

<section>
  <p class="section-title">일반 가전 — 삼성 vs LG</p>
  <div class="summary-wrap">
    <h3>카테고리별 평균 점수 (1년 평균)</h3>
    <div class="summary-bar-wrap"><canvas id="bar_trend"></canvas></div>
  </div>
  <div class="grid">{cards1}
  </div>
</section>

<hr class="divider">

<section style="margin-top:32px">
  <p class="section-title">구독 / 렌탈 — 삼성 vs LG vs 코웨이</p>
  <div class="summary-wrap">
    <h3>카테고리별 평균 점수 (1년 평균)</h3>
    <div class="summary-bar-wrap"><canvas id="bar_subscribe"></canvas></div>
  </div>
  <div class="grid">{cards2}
  </div>
</section>

<script>
{all_js}
{bar_js}
</script>
</body>
</html>"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n  ✔ 차트 저장 완료: {out_path}")
    return out_path


if __name__ == "__main__":
    main()
