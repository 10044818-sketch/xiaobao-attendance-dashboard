#!/usr/bin/env python3
"""
抓取指定日期范围内 A2 年级（行政班 A21 / A22）的缺勤记录。
复用 fetch_api.py 的登录与抓数函数，输出按天聚合的 a2_history.json。

环境变量：XIAOBAO_USER, XIAOBAO_PASS, START_DATE, END_DATE (YYYY-MM-DD)
"""
import os
import sys
import json
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_api import get_cookies, make_session, fetch_attendance_records, parse_api_rows

A2_PREFIX = "A2"
OUT_PATH = "a2_history.json"


def is_a2(cls):
    return str(cls or "").startswith(A2_PREFIX)


async def main():
    user = os.environ.get("XIAOBAO_USER")
    pwd = os.environ.get("XIAOBAO_PASS")
    start = os.environ.get("START_DATE", "2026-08-24")
    end = os.environ.get("END_DATE", "2026-09-08")
    if not user or not pwd:
        print("请设置 XIAOBAO_USER / XIAOBAO_PASS", file=sys.stderr)
        sys.exit(1)

    cookies = await get_cookies(user, pwd)
    session = make_session(cookies)

    out_days = []
    d = datetime.strptime(start, "%Y-%m-%d").date()
    end_d = datetime.strptime(end, "%Y-%m-%d").date()

    while d <= end_d:
        ds = d.isoformat()
        try:
            rows = fetch_attendance_records(session, ds)
            records = parse_api_rows(rows)
        except Exception as e:
            print(f"[warn] {ds} 抓取失败: {e}", file=sys.stderr)
            out_days.append({"date": ds, "ok": False, "students": [], "school_absent": 0})
            d += timedelta(days=1)
            continue

        school_absent = sum(1 for r in records if r.get("status") == "缺勤")
        by = {}
        for r in records:
            if r.get("status") != "缺勤":
                continue
            if not is_a2(r.get("admin_class")):
                continue
            name = r.get("name") or "未知"
            if name not in by:
                by[name] = {
                    "name": name,
                    "class": r.get("admin_class", ""),
                    "type": r.get("type", ""),
                    "reason": (r.get("leave_detail") or "").strip(),
                    "courses": [],
                }
            course = r.get("course", "")
            if course:
                by[name]["courses"].append({"course": course, "time": r.get("time_span", "")})

        out_days.append({
            "date": ds,
            "ok": True,
            "school_absent": school_absent,
            "students": list(by.values()),
        })
        print(f"{ds}: 全校缺勤 {school_absent} 条, A2 学生 {len(by)} 人", file=sys.stderr)
        d += timedelta(days=1)

    out = {"range": [start, end], "days": out_days}
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"已写出 {OUT_PATH}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
