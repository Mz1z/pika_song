import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

SITE_NAME = "闪闪-pika 的世界海"
SITE_SUBTITLE = "深海之下，是闪闪的星海"
SITE_DESCRIPTION = "闪闪-pika 的个人世界海：基本资料、直播间、小鱼日志、歌单与更多。"

LIVE_ROOM_ID = 1861308619
BILIBILI_SPACE = "https://space.bilibili.com/3546928222571136"
BILIBILI_LIVE = f"https://live.bilibili.com/{LIVE_ROOM_ID}"

LIVE_CACHE_TTL = 60
LIVE_API = "https://api.live.bilibili.com/room/v1/Room/get_info"
LIVE_ANCHOR_API = "https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room"

ADMIN_PASSWORD = os.environ.get("WORLDSEA_ADMIN_PASSWORD", "pika2026")
SECRET_KEY = os.environ.get("WORLDSEA_SECRET_KEY", "worldsea-sprinkle-pika-secret")

DB_PATH = os.path.join(BASE_DIR, "data", "worldsea.db")

PROFILE_DEFAULTS = {
    "name": "闪闪-pika",
    "en_name": "Sprinkle Pika",
    "avatar": "",
    "slogan": "愿每一次相遇，都像深海里的星光",
    "birthday": "20XX-XX-XX",
    "height": "??? cm",
    "debut_date": "20XX-XX-XX",
    "constellation": "双鱼座",
    "blood_type": "O 型",
    "hobby": "唱歌 / 打游戏 / 看海 / 摸鱼",
    "skills": "翻唱 / 中文歌 / 高音",
    "tags": "歌势,深海企划,闪闪,治愈系",
    "intro": (
        "来自深海世界的一尾小鱼，名字叫闪闪。\n"
        "喜欢在深蓝色的夜里唱歌，也喜欢把自己听到的故事唱给你们。\n"
        "这里是闪闪-pika 的世界海，欢迎每一位路过的旅人。"
    ),
    "room_name": "闪闪-pika 的直播间",
    "room_notice": "每晚与你在深海直播间相见，一起唱歌聊天看星星。",
    "room_schedule": "周一 / 周三 / 周五 / 周六 20:30 开播（以动态通知为准）",
}

LINK_DEFAULTS = [
    {"label": "Bilibili 主页", "url": BILIBILI_SPACE, "icon": "bi-house-heart-fill", "style": "pink"},
    {"label": "Bilibili 直播间", "url": BILIBILI_LIVE, "icon": "bi-broadcast", "style": "blue"},
    {"label": "网易云音乐", "url": "https://music.163.com/", "icon": "bi-music-note-beamed", "style": "red"},
    {"label": "QQ 群", "url": "#", "icon": "bi-people-fill", "style": "green"},
    {"label": "粉丝群 / 其他平台", "url": "#", "icon": "bi-link-45deg", "style": "teal"},
]

GALLERY_ITEMS = [
    {"title": "深海初见", "desc": "闪闪的第一张立绘", "emoji": "🐟", "gradient": "linear-gradient(135deg,#0077b6,#48cae4)"},
    {"title": "星海舞台", "desc": "直播间背景", "emoji": "🌟", "gradient": "linear-gradient(135deg,#023e8a,#00b4d8)"},
    {"title": "泡泡日常", "desc": "日常表情包", "emoji": "🫧", "gradient": "linear-gradient(135deg,#00b4d8,#90e0ef)"},
    {"title": "贝壳收藏", "desc": "周边设计稿", "emoji": "🐚", "gradient": "linear-gradient(135deg,#48cae4,#caf0f8)"},
    {"title": "夜色珊瑚", "desc": "演唱会海报", "emoji": "🪸", "gradient": "linear-gradient(135deg,#023e8a,#48cae4)"},
    {"title": "小鱼日志封面", "desc": "日志配图", "emoji": "📖", "gradient": "linear-gradient(135deg,#0096c7,#90e0ef)"},
]

UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads", "gallery")
ALLOWED_IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
