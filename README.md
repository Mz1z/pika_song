# 闪闪-pika 的世界海

闪闪-pika 的个人站「世界海」，海洋企划风格。包含基本资料、直播间实时状态、歌单、相册、小鱼日志、留言板，以及供闪闪使用的后台管理。

## 启动

```bash
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:5000`

## 页面模块

| 路径 | 说明 |
| --- | --- |
| `/` | 世界海首页 |
| `/profile` | 基本资料 |
| `/live` | 直播间（实时开播状态） |
| `/playlist` | 歌单（拿手 / 在学，翻页切换） |
| `/gallery` | 相册 |
| `/diary` | 小鱼日志 |
| `/board` | 留言板（留言需审核后显示） |
| `/links` | 联系 / 链接聚合 |
| `/admin` | 后台管理（需密码登录） |

## 后台管理

- 地址：`/admin`
- 默认密码：`pika2026`（在 `.env` 中通过 `WORLDSEA_ADMIN_PASSWORD` 修改）
- 功能：小鱼日志增删改、留言审核/删除、相册管理、基本资料与直播公告编辑

## 环境变量

首次部署时将 `.env.example` 复制为 `.env` 并修改（`.env` 已加入 `.gitignore`）：

```bash
cp .env.example .env
```

- `WORLDSEA_ADMIN_PASSWORD`：后台管理密码
- `WORLDSEA_SECRET_KEY`：Flask session 密钥

`.env` 会在启动时加载并**优先**于系统环境变量生效。生产环境请务必修改密码并设置随机密钥。

## 数据存储

- SQLite：`data/worldsea.db`（首次启动自动创建，已加入 `.gitignore`）
- 歌单缓存：`cache/*.json`
- 直播状态缓存：`cache/live_status.json`（60 秒）

## 技术栈

- Python Flask + requests
- SQLite（Python 自带 sqlite3）
- 网易云音乐公开 API、Bilibili 直播公开 API
- Bootstrap 5 + 原生 JS + Jinja2 多页面模板

## 配置

站点资料、直播排期、管理员密码、相册与友链等集中在 `config.py`；也可登录后台在线修改基本资料与直播公告。

## 图片素材

图片放在 `static/images/`：

- `head.png`：头像（首页 Hero、基本资料卡、直播间主播头像、站点图标）
- `pika.png`：全身立绘（首页 Hero、基本资料页）

当前为生成的占位图，直接用同名文件覆盖即可替换。若在后台「基本资料」中填写了头像地址，则优先显示该地址。

相册内容通过后台「相册管理」维护（可填图片地址或直接上传），上传的图片保存在 `static/uploads/gallery/`（已加入 `.gitignore`）。
