#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
네이버 데이터랩 API — 구독/렌탈 검색 트렌드 (삼성 vs LG vs 코웨이)
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
import os as _os
CLIENT_ID     = _os.environ.get("NAVER_CLIENT_ID",     "dXwlnIqtjUpjCCxXZuTK")
CLIENT_SECRET = _os.environ.get("NAVER_CLIENT_SECRET", "GPBMzhJhaS")
API_URL       = "https://openapi.naver.com/v1/datalab/search"
CALL_INTERVAL = 0.3

# ── 기간 설정 ─────────────────────────────────────────────
today      = datetime.today()
end_date   = today.strftime("%Y-%m-%d")
start_date = "2025-01-01"

# ── 카테고리 정의 ──────────────────────────────────────────
# three=True → 삼성/LG/코웨이 3자 비교
# three=False → 삼성/LG 2자 비교
CATEGORIES = [
    {
        "name": "구독브랜드", "three": True,
        "samsung": ["삼성구독", "삼성 가전 구독", "비스포크 구독", "삼성 렌탈"],
        "lg":      ["LG케어솔루션", "케어솔루션", "LG 구독", "LG 렌탈"],
        "coway":   ["코웨이", "코웨이 렌탈", "코웨이 구독"],
    },
    {
        "name": "정수기구독", "three": True,
        "samsung": ["삼성 정수기 렌탈", "비스포크 정수기 렌탈", "삼성 정수기 구독"],
        "lg":      ["LG 정수기 렌탈", "퓨리케어 렌탈", "LG 정수기 구독"],
        "coway":   ["코웨이 정수기", "코웨이 정수기 렌탈"],
    },
    {
        "name": "공기청정기구독", "three": True,
        "samsung": ["삼성 공기청정기 렌탈", "비스포크 공기청정기 렌탈"],
        "lg":      ["LG 공기청정기 렌탈", "퓨리케어 공기청정기 렌탈"],
        "coway":   ["코웨이 공기청정기", "코웨이 공기청정기 렌탈"],
    },
    {
        "name": "에어컨구독", "three": False,
        "samsung": ["삼성 에어컨 렌탈", "무풍에어컨 렌탈", "비스포크 에어컨 렌탈"],
        "lg":      ["LG 에어컨 렌탈", "휘센 에어컨 렌탈"],
    },
    {
        "name": "건조기구독", "three": False,
        "samsung": ["삼성 건조기 렌탈", "비스포크 건조기 렌탈"],
        "lg":      ["LG 건조기 렌탈", "트롬 건조기 렌탈"],
    },
    {
        "name": "세탁기구독", "three": False,
        "samsung": ["삼성 세탁기 렌탈", "비스포크 세탁기 렌탈"],
        "lg":      ["LG 세탁기 렌탈", "트롬 세탁기 렌탈"],
    },
    {
        "name": "식기세척기구독", "three": False,
        "samsung": ["삼성 식기세척기 렌탈", "비스포크 식기세척기 렌탈"],
        "lg":      ["LG 식기세척기 렌탈", "디오스 식기세척기 렌탈"],
    },
    {
        "name": "의류관리기구독", "three": False,
        "samsung": ["에어드레서 렌탈", "삼성 에어드레서 렌탈"],
        "lg":      ["스타일러 렌탈", "LG 스타일러 렌탈"],
    },
    {
        "name": "청소기구독", "three": False,
        "samsung": ["삼성 청소기 렌탈", "비스포크 제트 렌탈"],
        "lg":      ["LG 청소기 렌탈", "코드제로 렌탈"],
    },
    {
        "name": "로봇청소기구독", "three": False,
        "samsung": ["삼성 로봇청소기 렌탈", "비스포크 로봇청소기 렌탈"],
        "lg":      ["LG 로봇청소기 렌탈", "코드제로 로봇청소기 렌탈"],
    },
    {
        "name": "가전구독일반", "three": True,
        "samsung": ["삼성 가전 구독", "삼성 가전 렌탈", "삼성 구독 가전"],
        "lg":      ["LG 가전 구독", "LG 가전 렌탈", "LG 케어솔루션"],
        "coway":   ["코웨이 렌탈 추천", "코웨이 가격", "코웨이 렌탈 가격"],
    },
]

SAMSUNG_COLOR = "#1428A0"
LG_COLOR      = "#A50034"
COWAY_COLOR   = "#00A651"


def call_api(keyword_groups: list) -> dict:
    body = json.dumps({
        "startDate":     start_date,
        "endDate":       end_date,
        "timeUnit":      "month",
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
    if cat.get("three"):
        keyword_groups.append({"groupName": "코웨이", "keywords": cat["coway"]})
    data = call_api(keyword_groups)
    time.sleep(CALL_INTERVAL)
    return data


def process_results(data: dict) -> dict:
    out = {}
    for group in data.get("results", []):
        name = group["title"]
        out[name] = {r["period"]: r["ratio"] for r in group["data"]}
    return out


def determine_winner(avgs: dict) -> str:
    return max(avgs, key=avgs.get)


def main():
    today_str  = datetime.today().strftime("%Y%m%d")
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)

    summary_path = os.path.join(output_dir, f"subscribe_summary_{today_str}.csv")
    detail_path  = os.path.join(output_dir, f"subscribe_detail_{today_str}.csv")
    html_path    = os.path.join(output_dir, f"subscribe_report_{today_str}.html")

    all_results  = []
    summary_rows = []

    print(f"\n{'='*60}")
    print(f"  네이버 데이터랩 — 구독/렌탈 트렌드 (삼성 vs LG vs 코웨이)")
    print(f"  기간: {start_date} ~ {end_date}  |  단위: 월간")
    print(f"{'='*60}")

    for cat in CATEGORIES:
        label = "3자" if cat["three"] else "2자"
        print(f"  [{cat['name']}] API 호출 중 ({label})...", end=" ", flush=True)
        try:
            raw    = fetch_category(cat)
            parsed = process_results(raw)

            samsung_data = parsed.get("삼성",  {})
            lg_data      = parsed.get("LG",    {})
            coway_data   = parsed.get("코웨이", {}) if cat["three"] else {}
            periods      = sorted(samsung_data.keys())

            s_avg = round(sum(samsung_data.values()) / len(samsung_data), 2) if samsung_data else 0
            l_avg = round(sum(lg_data.values())      / len(lg_data),      2) if lg_data      else 0
            c_avg = round(sum(coway_data.values())   / len(coway_data),   2) if coway_data   else None

            avgs = {"삼성": s_avg, "LG": l_avg}
            if c_avg is not None:
                avgs["코웨이"] = c_avg

            winner = determine_winner(avgs)
            c_str  = f" vs 코웨이 {c_avg:.1f}" if c_avg is not None else ""
            print(f"완료  (삼성 {s_avg:.1f} vs LG {l_avg:.1f}{c_str}  →  {winner} 우세)")

            all_results.append({
                "name":    cat["name"],
                "three":   cat["three"],
                "periods": periods,
                "samsung": samsung_data,
                "lg":      lg_data,
                "coway":   coway_data,
                "s_avg":   s_avg,
                "l_avg":   l_avg,
                "c_avg":   c_avg,
                "winner":  winner,
            })
            row = {"카테고리": cat["name"], "삼성_평균": s_avg, "LG_평균": l_avg, "코웨이_평균": c_avg if c_avg is not None else "", "우세브랜드": winner}
            summary_rows.append(row)

        except URLError as e:
            print(f"실패: {e}")
            all_results.append({"name": cat["name"], "three": cat["three"], "periods": [], "samsung": {}, "lg": {}, "coway": {}, "s_avg": 0, "l_avg": 0, "c_avg": None, "winner": "N/A"})
            summary_rows.append({"카테고리": cat["name"], "삼성_평균": 0, "LG_평균": 0, "코웨이_평균": "", "우세브랜드": "N/A"})

    # ── CSV: Summary ──────────────────────────────────────
    with open(summary_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=["카테고리", "삼성_평균", "LG_평균", "코웨이_평균", "우세브랜드"])
        writer.writeheader()
        writer.writerows(summary_rows)

    # ── CSV: Detail ───────────────────────────────────────
    all_periods = sorted({p for r in all_results for p in r["periods"]})
    with open(detail_path, "w", newline="", encoding="utf-8-sig") as f:
        fieldnames = ["카테고리", "브랜드"] + all_periods
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in all_results:
            for brand, bdata in [("삼성", r["samsung"]), ("LG", r["lg"])]:
                row = {"카테고리": r["name"], "브랜드": brand}
                for p in all_periods:
                    row[p] = bdata.get(p, "")
                writer.writerow(row)
            if r["three"] and r["coway"]:
                row = {"카테고리": r["name"], "브랜드": "코웨이"}
                for p in all_periods:
                    row[p] = r["coway"].get(p, "")
                writer.writerow(row)

    # ── HTML Report ───────────────────────────────────────
    charts_js = []
    for i, r in enumerate(all_results):
        periods_json = json.dumps(r["periods"])
        s_json = json.dumps([r["samsung"].get(p, 0) for p in r["periods"]])
        l_json = json.dumps([r["lg"].get(p, 0) for p in r["periods"]])

        datasets = f"""
                    {{ label: '삼성', data: {s_json}, borderColor: '{SAMSUNG_COLOR}', backgroundColor: '{SAMSUNG_COLOR}22', tension: 0.3, fill: true }},
                    {{ label: 'LG',   data: {l_json}, borderColor: '{LG_COLOR}',      backgroundColor: '{LG_COLOR}22',      tension: 0.3, fill: true }}"""

        if r["three"] and r["coway"]:
            c_json  = json.dumps([r["coway"].get(p, 0) for p in r["periods"]])
            datasets += f""",
                    {{ label: '코웨이', data: {c_json}, borderColor: '{COWAY_COLOR}', backgroundColor: '{COWAY_COLOR}22', tension: 0.3, fill: true }}"""

        charts_js.append(f"""
        new Chart(document.getElementById('chart_{i}'), {{
            type: 'line',
            data: {{
                labels: {periods_json},
                datasets: [{datasets}]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '{r["name"]}' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});""")

    bar_labels  = json.dumps([r["name"] for r in all_results])
    bar_samsung = json.dumps([r["s_avg"] for r in all_results])
    bar_lg      = json.dumps([r["l_avg"] for r in all_results])
    bar_coway   = json.dumps([r["c_avg"] if r["c_avg"] is not None else 0 for r in all_results])

    charts_js.append(f"""
        new Chart(document.getElementById('chart_summary'), {{
            type: 'bar',
            data: {{
                labels: {bar_labels},
                datasets: [
                    {{ label: '삼성 평균', data: {bar_samsung}, backgroundColor: '{SAMSUNG_COLOR}CC' }},
                    {{ label: 'LG 평균',   data: {bar_lg},      backgroundColor: '{LG_COLOR}CC' }},
                    {{ label: '코웨이 평균', data: {bar_coway},  backgroundColor: '{COWAY_COLOR}CC' }}
                ]
            }},
            options: {{ responsive: true, plugins: {{ title: {{ display: true, text: '전체 카테고리 평균 점수 비교' }} }}, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});""")

    category_cards = ""
    winner_colors  = {"삼성": SAMSUNG_COLOR, "LG": LG_COLOR, "코웨이": COWAY_COLOR}
    for i, r in enumerate(all_results):
        wc    = winner_colors.get(r["winner"], "#333")
        c_str = f" vs 코웨이 {r['c_avg']:.1f}" if r["c_avg"] is not None else ""
        category_cards += f"""
        <div class="card">
            <canvas id="chart_{i}"></canvas>
            <p class="winner" style="color:{wc}">▶ {r['winner']} 우세 (삼성 {r['s_avg']:.1f} vs LG {r['l_avg']:.1f}{c_str})</p>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>네이버 트렌드 — 구독/렌탈 (삼성 vs LG vs 코웨이) {today_str}</title>
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
<h1>📊 네이버 검색 트렌드 — 구독/렌탈 (삼성 vs LG vs 코웨이)</h1>
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
    print(f"\n{'='*64}")
    print(f"  카테고리별 우세 브랜드 요약")
    print(f"{'='*64}")
    print(f"  {'카테고리':<14}  {'삼성':>6}  {'LG':>6}  {'코웨이':>6}  {'우세':>6}")
    print(f"  {'-'*52}")
    wins = {"삼성": 0, "LG": 0, "코웨이": 0}
    for r in all_results:
        c_str = f"{r['c_avg']:>6.1f}" if r["c_avg"] is not None else f"{'—':>6}"
        print(f"  {r['name']:<14}  {r['s_avg']:>6.1f}  {r['l_avg']:>6.1f}  {c_str}  {r['winner']:>6}")
        if r["winner"] in wins:
            wins[r["winner"]] += 1
    print(f"  {'-'*52}")
    print(f"  전체 우세: 삼성 {wins['삼성']}개 / LG {wins['LG']}개 / 코웨이 {wins['코웨이']}개")
    print(f"{'='*64}")
    print(f"\n  저장 완료:")
    print(f"    {summary_path}")
    print(f"    {detail_path}")
    print(f"    {html_path}\n")


if __name__ == "__main__":
    main()
