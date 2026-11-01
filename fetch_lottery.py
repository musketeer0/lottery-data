# -*- coding: utf-8 -*-
"""
抓取「大乐透(体彩) + 双色球(福彩)」最新历史开奖数据，输出 lottery_data.json。

设计用途：在服务端（如 GitHub Actions 定时任务）运行。服务端 HTTP 请求不受浏览器 CORS 限制，
只要带上正确的 User-Agent / Referer 头即可直接读取官方接口。

依赖：仅 Python 3 标准库（urllib），无需 pip install。

输出 JSON 结构（供前端直接使用）：
{
  "updated": "2026-11-01T12:00:00Z",
  "dlt":  { "latest": "26124", "list": [ { "q": "26124", "f": [12,14,18,22,27], "b": [1,9], "d": "2026-10-31" }, ... ] },
  "ssq":  { "latest": "2026124", "list": [ { "q": "2026124", "f": [3,11,17,22,23,29], "b": 9, "d": "2026-10-29" }, ... ] }
}
"""
import json
import urllib.request
from datetime import datetime, timezone

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def http_get(url, referer=None, timeout=30):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", UA)
    req.add_header("Accept", "application/json, text/plain, */*")
    req.add_header("Accept-Language", "zh-CN,zh;q=0.9")
    if referer:
        req.add_header("Referer", referer)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_dlt(count=120):
    """大乐透：体彩官方接口，必须带 Referer 头"""
    url = ("https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
           "?gameNo=85&provinceId=0&pageSize=%d&isVerify=1&pageNo=1" % count)
    j = http_get(url, referer="https://www.lottery.gov.cn/")
    out = []
    for it in (j.get("value", {}).get("list") or []):
        nums = [int(x) for x in str(it.get("lotteryDrawResult", "")).split()]
        if len(nums) >= 7:
            out.append({
                "q": str(it.get("lotteryDrawNum")),
                "f": nums[:5],
                "b": nums[5:7],
                "d": str(it.get("lotteryDrawTime", ""))[:10],
            })
    return out


def fetch_ssq(count=120):
    """双色球：中彩网官方接口"""
    url = ("https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice"
           "?name=ssq&issueCount=%d" % count)
    j = http_get(url)
    out = []
    for it in (j.get("result") or []):
        red = [int(x) for x in str(it.get("red", "")).split(",") if x]
        blue = int(it.get("blue", 0) or 0)
        if len(red) == 6 and blue > 0:
            out.append({
                "q": str(it.get("code")),
                "f": red,
                "b": blue,
                "d": str(it.get("date", ""))[:10],
            })
    return out


def main():
    dlt = fetch_dlt()
    ssq = fetch_ssq()
    data = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dlt": {"latest": dlt[0]["q"] if dlt else "", "list": dlt},
        "ssq": {"latest": ssq[0]["q"] if ssq else "", "list": ssq},
    }
    with open("lottery_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("updated:", data["updated"])
    print("dlt :", len(dlt), "期, 最新", data["dlt"]["latest"])
    print("ssq :", len(ssq), "期, 最新", data["ssq"]["latest"])


if __name__ == "__main__":
    main()
