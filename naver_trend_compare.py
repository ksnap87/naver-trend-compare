#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 데이터랩 API — 일반 가전 검색 트렌드 (삼성 vs LG)
"""

import json
import time
import csv
import os
import ssl
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError

# macOS SSL 인증서 문제 우회
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# ── API 설정 ──────────────────────────────────────────────
CLIENT_ID     = "dXwlnIqtjUpjCCxXZuTK"
CLIENT_SECRET = "GPBMzhJhaS"
API_URL       = "https://openapi.naver.com/v1/datalab/search"
CALL_INTERVAL = 0.3  # seconds

# ── 기간 설정 (최근 1년, 월간) ─────────────────────────────
today     = datetime.today()
end_date  = today.strftime("%Y-%m-%d")
start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")

# ── 카테고리 정의 ──────────────────────────────────────────
CATEGORIES = [
    {
        "name": "냉장고",
        "samsung": ["삼성냉장고", "삼성 냉장고", "비스포크냉장고", "비스포크 냉장고", "삼성 냉장고 추천"],
        "lg":      ["LG냉장고", "LG 냉장고", "오브제냉장고", "LG 오브제 냉장고", "LG 냉장고 추천"],
    },
    {
        "name": "세탁기",
        "samsung": ["삼성세탁기", "삼성 세탁기", "비스포크세탁기", "비스포크 세탁기", "삼성 그랑데"],
        "lg":      ["LG세탁기", "LG 세탁기", "LG트롬", "LG 트롬 세탁기", "트롬세탁기"],
    },
    {
        "name": "에어컨",
        "samsung": ["삼성에어컨", "삼성 에어컨", "무풍에어컨", "비스포크에어컨", "비스포크 에어컨"],
        "lg":      ["LG에어컨", "LG 에어컨", "휘센에어컨", "LG휘센", "LG 휘센 에어컨"],
    },
    {
        "name": "TV",
        "samsung": ["삼성TV", "삼성 TV", "네오QLED", "삼성 네오QLED", "삼성 QLED"],
        "lg":      ["LGTV", "LG TV", "LG OLED", "LG 올레드", "LG OLED TV"],
    },
    {
        "name": "건조기",
        "samsung": ["삼성건조기", "삼성 건조기", "비스포크건조기", "비스포크 건조기", "삼성 그랑데 건조기"],
        "lg":      ["LG건조기", "LG 건조기", "LG트롬건조기", "LG 트롬 건조기", "트롬건조기"],
    },
    {
        "name": "정수기",
        "samsung": ["삼성정수기", "삼성 정수기", "비스포크정수기", "비스포크 정수기", "삼성 정수기 렌탈"],
        "lg":      ["LG정수기", "LG 정수기", "퓨리케어정수기", "LG 퓨리케어", "LG 정수기 렌탈"],
    },
    {
        "name": "공기청정기",
        "samsung": ["삼성공기청정기", "삼성 공기청정기", "비스포크 공기청정기", "비스포크공기청정기"],
        "lg":      ["LG공기청정기", "LG 공기청정기", "LG 퓨리케어 공기청정기", "퓨리케어 공기청정기"],
    },
    {
        "name": "식기세척기",
        "samsung": ["삼성식기세척기", "삼성 식기세척기", "비스포크식기세척기", "비스포크 식기세척기"],
        "lg":      ["LG식기세척기", "LG 식기세척기", "LG디오스식기세척기", "LG 디오스 식기세척기"],
    },
    {
        "name": "청소기",
        "samsung": ["삼성청소기", "삼성 청소기", "비스포크제트", "비스포크 제트", "삼성 제트"],
        "lg":      ["LG청소기", "LG 청소기", "코드제로", "LG코드제로", "LG 코드제로"],
    },
    {
        "name": "로봇청소기",
        "samsung": ["삼성 로봇청소기", "비스포크 로봇청소기", "삼성 로봇청소기 추천"],
        "lg":      ["LG 로봇청소기", "코드제로 로봇청소기", "LG 로봇청소기 추천"],
    },
    {
        "name": "의류관리기",
        "samsung": ["에어드레서", "삼성에어드레서", "삼성 에어드레서", "비스포크 에어드레서"],
        "lg":      ["LG스타일러", "LG 스타일러", "스타일러", "LG 의류관리기"],
    },
]

SAMSUNG_COLOR = "#1428A0"
LG_COLOR      = "#A50034"


def call_api(keyword_groups: list) -> dict:
    body = json.dumps({
        "startDate":  start_date,
        "endDate":    end_date,
        "timeUnit":   "month",
        "keywordGroups": keyword_groups,
    }, ensure_ascii=False).encode("utf-8")

    req = Request(API_URL, data=body)
    req.add_header("X-Naver-Client-Id",     CLIENT_ID)
    req.add_header("X-Naver-Client-Secret", CLIENT_SECRET)
    req.add_header("Content-Type",          "application/json")

    with urlopen(req, context=SSL_CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_category(cat: dict) -> dict:
    keyword_groups = [
        {"groupName": "삼성", "keywords": cat["samsung"]},
        {"groupName": "LG",   "keywords": cat["lg"]},
    ]
    data = call_api(keyword_groups)
    time.sleep(CALL_INTERVAL)
    return data


def avg_ratio(results_list: list) -> float:
    vals = [r["ratio"] for r in results_list]
    return round(sum(vals) / len(vals), 2) if vals else 0.0


def process_results(data: dict) -> dict:
    """결과를 {brand: {period: ratio}} 형태로 변환"""
    out = {}
    for group in data.get("results", []):
        name = group["title"]
        out[name] = {r["period"]: r["ratio"] for r in group["data"]}
    return out


def main():
    today_str = datetime.today().strftime("%Y%m%d")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    summary_path = os.path.join(output_dir, f"trend_summary_{today_str}.csv")
    detail_path  = os.path.join(output_dir, f"trend_detail_{today_str}.csv")
    html_path    = os.path.join(output_dir, f"trend_report_{today_str}.html")

    all_results = []   # [{name, periods, samsung_data, lg_data}]
    summary_rows = []  # [{category, samsung_avg, lg_avg, winner}]

    print(f"\n{'='*60}")
    print(f"  네이버 데이터랩 — 일반 가전 트렌드 (삼성 vs LG)")
    print(f"  기간: {start_date} ~ {end_date}  |  단위: 월간")
    print(f"{'='*60}")

    for cat in CATEGORIES:
        print(f"  [{cat['name']}] API 호출 중...", end=" ", flush=True)
        try:
            raw = fetch_category(cat)
            parsed = process_results(raw)

            samsung_data = parsed.get("삼성", {})
            lg_data      = parsed.get("LG", {})
            periods      = sorted(samsung_data.keys())

            s_avg = avg_ratio(list({"period": p, "ratio": samsung_data[p]} for p in periods))
            l_avg = avg_ratio(list({"period": p, "ratio": lg_data.get(p, 0)} for p in periods))
            s_avg = round(sum(samsung_data.values()) / len(samsung_data), 2) if samsung_data else 0
            l_avg = round(sum(lg_data.values())      / len(lg_data),      2) if lg_data      else 0

            winner = "삼성" if s_avg >= l_avg else "LG"
            print(f"완료  (삼성 {s_avg:.1f} vs LG {l_avg:.1f}  →  {winner} 우세)")

            all_results.append({
                "name":        cat["name"],
                "periods":     periods,
                "samsung":     samsung_data,
                "lg":          lg_data,
                "samsung_avg": s_avg,
                "lg_avg":      l_avg,
                "winner":      winner,
            })
            summary_rows.append({
                "카테고리": cat["name"],
                "삼성_평균": s_avg,
                "LG_평균":   l_avg,
                "우세브랜드": winner,
            })
        except URLError as e:
            print(f"실패: {e}")
            all_results.append({"name": cat["name"], "periods": [], "samsung": {}, "lg": {}, "samsung_avg": 0, "lg_avg": 0, "winner": "N/A"})
            summary_rows.append({"카테고리": cat["name"], "삼성_평균": 0, "LG_평균": 0, "우세브랜드": "N/A"})

    # ── CSV: Summary ──────────────────────────────────────
    with open(summary_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["카테고리", "삼성_평균", "LG_평균", "우세브랜드"])
        writer.writeheader()
        writer.writerows(summary_rows)

    # ── CSV: Detail ───────────────────────────────────────
    all_periods = sorted({p for r in all_results for p in r["periods"]})
    with open(detail_path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["카테고리", "브랜드"] + all_periods
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            row_s = {"카테고리": r["name"], "브랜드": "삼성"}
            row_l = {"카테고리": r["name"], "브랜드": "LG"}
            for p in all_periods:
                row_s[p] = r["samsung"].get(p, "")
                row_l[p] = r["lg"].get(p, "")
            writer.writerow(row_s)
            writer.writerow(row_l)

    # ── HTML Report ───────────────────────────────────────
    charts_js = []
    for i, r in enumerate(all_results):
        periods_json  = json.dumps(r["periods"])
        samsung_json  = json.dumps([r["samsung"].get(p, 0) for p in r["periods"]])
        lg_json       = json.dumps([r["lg"].get(p, 0) for p in r["periods"]])
        charts_js.append(f"""
        new Chart(document.getElementById('chart_{i}'), {{
            type: 'line',
            data: {{
                labels: {periods_json},
                datasets: [
                    {{ label: '삼성', data: {samsung_json}, borderColor: '{SAMSUNG_COLOR}', backgroundColor: '{SAMSUNG_COLOR}22', tension: 0.3, fill: true }},
                    {{ label: 'LG',   data: {lg_json},      borderColor: '{LG_COLOR}',      backgroundColor: '{LG_COLOR}22',      tension: 0.3, fill: true }}
                ]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '{r["name"]}' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});""")

    bar_labels  = json.dumps([r["name"] for r in all_results])
    bar_samsung = json.dumps([r["samsung_avg"] for r in all_results])
    bar_lg      = json.dumps([r["lg_avg"] for r in all_results])

    charts_js.append(f"""
        new Chart(document.getElementById('chart_summary'), {{
            type: 'bar',
            data: {{
                labels: {bar_labels},
                datasets: [
                    {{ label: '삼성 평균', data: {bar_samsung}, backgroundColor: '{SAMSUNG_COLOR}CC' }},
                    {{ label: 'LG 평균',   data: {bar_lg},      backgroundColor: '{LG_COLOR}CC' }}
                ]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '전체 카테고리 평균 점수 비교' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});""")

    category_cards = ""
    for i, r in enumerate(all_results):
        winner_color = SAMSUNG_COLOR if r["winner"] == "삼성" else LG_COLOR
        category_cards += f"""
        <div class="card">
            <canvas id="chart_{i}"></canvas>
            <p class="winner" style="color:{winner_color}">▶ {r['winner']} 우세 (삼성 {r['samsung_avg']:.1f} vs LG {r['lg_avg']:.1f})</p>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>네이버 트렌드 — 일반 가전 (삼성 vs LG) {today_str}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body {{ font-family: 'Malgun Gothic', sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
  h1 {{ text-align: center; color: #333; }}
  .subtitle {{ text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(480px, 1fr)); gap: 20px; }}
  .card {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .winner {{ text-align: center; font-weight: bold; margin-top: 8px; font-size: 14px; }}
  .summary-card {{ background: #fff; border-radius: 10px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 24px; }}
</style>
</head>
<body>
<h1>📊 네이버 검색 트렌드 — 일반 가전 (삼성 vs LG)</h1>
<p class="subtitle">기간: {start_date} ~ {end_date} | 단위: 월간 | 생성일: {today_str}</p>
<div class="summary-card"><canvas id="chart_summary"></canvas></div>
<div class="grid">{category_cards}
</div>
<script>
    {chr(10).join(charts_js)}
</script>
</body>
</html>"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    # ── 콘솔 요약표 ──────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"  카테고리별 우세 브랜드 요약")
    print(f"{'='*60}")
    print(f"  {'카테고리':<12}  {'삼성 평균':>8}  {'LG 평균':>8}  {'우세':>6}")
    print(f"  {'-'*44}")
    samsung_wins = lg_wins = 0
    for r in all_results:
        marker = "◀" if r["winner"] == "삼성" else "  "
        print(f"  {r['name']:<12}  {r['samsung_avg']:>8.1f}  {r['lg_avg']:>8.1f}  {r['winner']:>4} {marker}")
        if r["winner"] == "삼성": samsung_wins += 1
        else: lg_wins += 1
    print(f"  {'-'*44}")
    print(f"  전체 우세: 삼성 {samsung_wins}개 / LG {lg_wins}개")
    print(f"{'='*60}")
    print(f"\n  저장 완료:")
    print(f"    {summary_path}")
    print(f"    {detail_path}")
    print(f"    {html_path}\n")


if __name__ == "__main__":
    main()
