# 闪闪-pika 的歌单

展示闪闪-pika 在网易云音乐的拿手歌单和在学歌单。

## 启动

```bash
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:5000`

## 功能

- 切换查看**拿手歌单** / **在学歌单**（翻页动画）
- 强制刷新（绕过 10 分钟本地缓存）
- 跳转 Bilibili 主页和直播间

## 技术栈

- Python Flask + requests
- 网易云音乐公开 API
- Bootstrap 5 + 原生 JS
