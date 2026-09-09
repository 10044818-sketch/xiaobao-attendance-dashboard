# 每日出勤看板

从校宝系统每小时自动抓取学生出勤数据，生成类似图片样式的在线看板。

## 数据来源

- 校宝系统：https://ray.schoolis.cn
- 抓取范围：学生上课考勤记录（今日）
- 操作性质：**只读**，不会修改任何校宝数据

## 项目文件

- `index.html`：看板前端页面
- `data.json`：今日出勤数据（由脚本自动生成）
- `fetch_api.py`：登录校宝并调用内部 API 抓取数据
- `requirements.txt`：Python 依赖
- `.github/workflows/update.yml`：GitHub Actions 每小时自动更新并部署

## 部署步骤（GitHub Pages）

1. 在 GitHub 创建**公开仓库**（例如 `xiaobao-attendance-dashboard`）
   - 注意：GitHub Pages 免费站点需要仓库为 Public
2. 将本目录下所有文件 push 到仓库
3. 进入仓库 Settings → Secrets and variables → Actions，添加：
   - `XIAOBAO_USER`：校宝登录账号
   - `XIAOBAO_PASS`：校宝登录密码
4. 进入 Settings → Pages，Source 选择 "GitHub Actions"
5. 进入 Actions → Update Xiaobao Attendance Dashboard，点击 "Run workflow" 手动触发一次
6. 等待 workflow 完成后，看板地址：
   `https://<你的用户名>.github.io/xiaobao-attendance-dashboard`

## 本地测试

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
XIAOBAO_USER=<账号> XIAOBAO_PASS=<密码> python fetch_api.py
python -m http.server 8123
```

然后访问 http://localhost:8123
