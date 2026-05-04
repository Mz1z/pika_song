import requests
import json
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://music.163.com/",
}

LEARNING_PLAYLIST_ID = "17849227734"
SKILLED_PLAYLIST_ID = "17884494363"

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
CACHE_TTL = 600

os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(playlist_type):
    return os.path.join(CACHE_DIR, f"{playlist_type}.json")


def _read_cache(playlist_type):
    path = _cache_path(playlist_type)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            cached = json.load(f)
        if time.time() - cached.get("ts", 0) < CACHE_TTL:
            return cached["data"]
    except Exception:
        pass
    return None


def _write_cache(playlist_type, data):
    path = _cache_path(playlist_type)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"ts": time.time(), "data": data}, f, ensure_ascii=False)
    except Exception:
        pass


API_URL = "https://music.163.com/api/playlist/detail?id={}"


def _fetch_playlist_api(playlist_id):
    try:
        resp = requests.get(API_URL.format(playlist_id), headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 200 and "result" in data:
                return data["result"]
    except Exception:
        pass
    return None


def _get_test_data(playlist_name, tracks_count=10):
    test_songs = [
        {"name": "歌单接口坏了", "artist": "快去叫Mz1", "album": "oh no!"},
    ]
    tracks = []
    for i, song in enumerate(test_songs[:tracks_count]):
        tracks.append({
            "id": str(i + 1),
            "name": song["name"],
            "artist": song["artist"],
            "album": song["album"],
        })

    return {
        "playlist_name": playlist_name,
        "track_count": len(tracks),
        "tracks": tracks,
        "source": "测试数据（网易云API未获取到真实数据）",
    }


def get_playlist(playlist_type, force_refresh=False):
    playlist_id = LEARNING_PLAYLIST_ID if playlist_type == "learning" else SKILLED_PLAYLIST_ID
    playlist_name = "在学歌单" if playlist_type == "learning" else "拿手歌单"

    if not force_refresh:
        cached = _read_cache(playlist_type)
        if cached:
            return cached

    result = _fetch_playlist_api(playlist_id)
    if result:
        tracks = []
        for track in result.get("tracks", []):
            tracks.append({
                "id": str(track.get("id", "")),
                "name": track.get("name", ""),
                "artist": "/".join(a["name"] for a in track.get("artists", [])),
                "album": track.get("album", {}).get("name", ""),
            })
        data = {
            "playlist_name": result.get("name", playlist_name),
            "track_count": result.get("trackCount", len(tracks)),
            "tracks": tracks,
            "source": "网易云音乐实时数据",
        }
    else:
        data = _get_test_data(playlist_name)

    _write_cache(playlist_type, data)
    return data
