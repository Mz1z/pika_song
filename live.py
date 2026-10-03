import json
import os
import time

import requests

from config import LIVE_API, LIVE_ANCHOR_API, LIVE_CACHE_TTL, LIVE_ROOM_ID

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://live.bilibili.com/",
}

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_FILE = os.path.join(CACHE_DIR, "live_status.json")

STATUS_TEXT = {0: "未开播", 1: "直播中", 2: "轮播中"}


def _default_status():
    return {
        "room_id": LIVE_ROOM_ID,
        "live_status": 0,
        "status_text": STATUS_TEXT[0],
        "title": "等待开播中",
        "cover": "",
        "online": 0,
        "area": "",
        "live_time": "",
        "anchor_name": "闪闪-pika",
        "anchor_face": "",
        "updated_at": int(time.time()),
        "source": "default",
    }


def _read_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if time.time() - cached.get("ts", 0) < LIVE_CACHE_TTL:
            return cached.get("data")
    except Exception:
        pass
    return None


def _write_cache(data):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "data": data}, f, ensure_ascii=False)
    except Exception:
        pass


def _fetch_live_info(room_id):
    resp = requests.get(
        LIVE_API,
        params={"room_id": room_id},
        headers=HEADERS,
        timeout=10,
    )
    payload = resp.json()
    if payload.get("code") != 0 or not payload.get("data"):
        return None
    return payload["data"]


def _fetch_anchor(room_id):
    try:
        resp = requests.get(
            LIVE_ANCHOR_API,
            params={"roomid": room_id},
            headers=HEADERS,
            timeout=10,
        )
        payload = resp.json()
        if payload.get("code") != 0:
            return None
        info = (payload.get("data") or {}).get("info") or {}
        return {"name": info.get("uname", ""), "face": info.get("face", "")}
    except Exception:
        return None


def get_live_status(force_refresh=False):
    if not force_refresh:
        cached = _read_cache()
        if cached:
            return cached

    data = _default_status()
    try:
        info = _fetch_live_info(LIVE_ROOM_ID)
        if info:
            live_status = info.get("live_status", 0)
            data.update(
                {
                    "live_status": live_status,
                    "status_text": STATUS_TEXT.get(live_status, "未知"),
                    "title": info.get("title") or "等待开播中",
                    "cover": info.get("cover", ""),
                    "online": info.get("online", 0),
                    "area": info.get("area_name", "") or info.get("parent_area_name", ""),
                    "live_time": info.get("live_time", ""),
                    "source": "bilibili",
                }
            )
            anchor = _fetch_anchor(LIVE_ROOM_ID)
            if anchor and anchor.get("name"):
                data["anchor_name"] = anchor["name"]
                data["anchor_face"] = anchor.get("face") or data["anchor_face"]
    except Exception:
        data = _default_status()

    data["updated_at"] = int(time.time())
    if data.get("source") == "bilibili":
        _write_cache(data)
    return data
