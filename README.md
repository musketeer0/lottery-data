# 乐透智选 · 开奖数据（定时抓取 → GitHub → jsDelivr）

解决两个问题：
1. 浏览器直连官方接口被 CORS 拦截；
2. GitHub Actions（海外 IP）被体彩接口 **HTTP 567** 拦截（地域限制）。

方案：用**你本机（国内 IP）的 Windows 计划任务**每天抓一次，推到 GitHub，前端经 jsDelivr（自带 CORS 头）读取。

## 架构

```
[你的电脑·国内 IP] --每天21:35--> fetch_lottery.py --> lottery_data.json --> git push --> GitHub 仓库
                                                                                          |
前端(秒哒) --fetch--> jsDelivr CDN  https://cdn.jsdelivr.net/gh/musketeer0/lottery-data@main/lottery_data.json
```

## 文件

| 文件 | 作用 |
| --- | --- |
| `fetch_lottery.py` | 抓取大乐透 + 双色球官方数据，输出 `lottery_data.json`（仅标准库） |
| `update_data.bat` | 计划任务入口：抓取 → git 提交 → 推送到 GitHub |
| `lottery_data.json` | 抓取结果（前端读取的数据） |

## 数据源（需国内 IP）

- **大乐透**：`webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85`，须带 `Referer: https://www.lottery.gov.cn/`
- **双色球**：`www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq`

> 两个接口都对海外 IP 有地域限制（体彩返回 HTTP 567），所以必须在国内 IP 下运行。这也是为什么不用 GitHub Actions 而用本机计划任务。

## 定时任务

已创建 Windows 计划任务 `LotteryDataUpdate`，每天 **21:35** 运行 `update_data.bat`（覆盖当天开奖）。

- 查看：`schtasks /query /tn LotteryDataUpdate`
- 手动跑一次：直接双击 `update_data.bat`，或 `schtasks /run /tn LotteryDataUpdate`
- 删除：`schtasks /delete /tn LotteryDataUpdate /f`

> 计划任务只在「用户已登录」时运行；关机/未登录当天会跳过，下次到点再跑，数据最坏延迟一天，不影响使用。

## 前端

前端 HTML 的 `DATA_JSON_URL` 已指向：
`https://cdn.jsdelivr.net/gh/musketeer0/lottery-data@main/lottery_data.json`

jsDelivr 对 `@main` 有约 12 小时缓存；想更快刷新可用 raw 直链（缓存更短）：
`https://raw.githubusercontent.com/musketeer0/lottery-data/main/lottery_data.json`

## 安全提示

本机 git 远程地址内嵌了 GitHub token，用完后建议去 GitHub 上 Revoke 该 token，或换成专属最小权限 token。
