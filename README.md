# 乐透智选 · 开奖数据后端（定时抓取）

解决浏览器跨域（CORS）拿不到官方开奖数据的问题：把「抓取」搬到服务端（GitHub Actions 定时任务），
生成一个 `lottery_data.json`，前端通过 jsDelivr CDN 读取（jsDelivr 自带 `Access-Control-Allow-Origin: *`，浏览器可直接跨域）。

## 文件说明

| 文件 | 作用 |
| --- | --- |
| `fetch_lottery.py` | 抓取大乐透 + 双色球官方数据，输出 `lottery_data.json`（仅用 Python 标准库） |
| `.github/workflows/update-data.yml` | 定时任务：每天北京时间 21:30 自动运行脚本并提交数据 |
| `lottery_data.json` | 抓取结果（由脚本生成，已随本次提交） |

## 数据源

- **大乐透（体彩）**：`webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry?gameNo=85`
  - ⚠️ 必须带请求头 `Referer: https://www.lottery.gov.cn/`，否则返回反爬 HTML 而非 JSON。
- **双色球（福彩）**：`www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq`
  - 直接 GET 返回 JSON。

> 服务端请求**没有 CORS 限制**（CORS 是浏览器专属的安全机制），所以放在 GitHub Actions 里跑没有任何跨域问题。

## 部署步骤

1. 在 GitHub 新建一个**公开**仓库（例如 `lottery-data`）。
2. 把本目录的 `fetch_lottery.py`、`.github/workflows/update-data.yml`、`lottery_data.json` 三个文件推送到仓库根目录（`.github/workflows/` 在根目录下）。
3. 打开仓库 **Settings → Actions → General**，确认 Workflow permissions 勾选 **Read and write permissions**（工作流里已声明 `permissions: contents: write`，一般无需额外改动）。
4. 打开 **Actions** 页，手动跑一次 `Update lottery data` 验证能成功生成/更新数据。

## 让前端读到数据

前端 HTML 里有一行（在脚本的 `loadLiveData` 上方）：

```js
var DATA_JSON_URL='https://cdn.jsdelivr.net/gh/YOUR_USERNAME/YOUR_REPO@main/lottery_data.json';
```

把 `YOUR_USERNAME/YOUR_REPO` 换成你的 GitHub 用户名和仓库名即可。之后打开页面会自动从该地址读取最新数据；
读取失败会自动回退到 HTML 内置数据，不影响使用。

## 常见问题

- **jsDelivr 有缓存**：jsDelivr 对 `@main` 的缓存约 12 小时，最长 24 小时。若想更快看到新数据，可用 `@latest`（仍需等待刷新）或直接改用 GitHub Raw（`https://raw.githubusercontent.com/USER/REPO/main/lottery_data.json`，也带 CORS 头，缓存更短）。
- **每天只抓一次够不够**：大乐透周一/三/六开奖，双色球周二/四/日开奖；每天 21:30 抓取已覆盖当天开奖。如需更频繁，把 cron 改成每天多次即可。
- **想不用 GitHub**：也可以用任何能跑 Python 的服务器/云函数（如 Cloudflare Worker、Vercel、自建 VPS）运行 `fetch_lottery.py`，把 `lottery_data.json` 放到任意带 CORS 头的静态托管即可。
