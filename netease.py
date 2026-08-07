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


POST_HEADERS = {
    **HEADERS,
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://music.163.com",
}


def _fetch_playlist_api(playlist_id):
    """获取歌单完整数据。

    1. POST /api/v6/playlist/detail 获取歌单信息及全部 trackIds
    2. POST /api/v3/song/detail 按 trackIds 批量获取歌曲完整信息

    返回 {playlist_name, track_count, tracks} 或 None
    """
    try:
        detail_resp = requests.post(
            "https://music.163.com/api/v6/playlist/detail",
            data={"id": str(playlist_id), "n": "100000", "s": "8"},
            headers=POST_HEADERS,
            timeout=30,
        )
        detail = detail_resp.json()
        if detail.get("code") != 200 or not detail.get("playlist"):
            return None
        playlist = detail["playlist"]
        track_ids = [t["id"] for t in (playlist.get("trackIds") or [])]
        if not track_ids:
            return {
                "playlist_name": playlist.get("name", ""),
                "track_count": playlist.get("trackCount", 0),
                "tracks": [],
            }

        songs = []
        for i in range(0, len(track_ids), 200):
            batch = track_ids[i:i + 200]
            c = json.dumps([{"id": sid} for sid in batch])
            song_resp = requests.post(
                "https://music.163.com/api/v3/song/detail",
                data={"c": c, "ids": json.dumps(batch)},
                headers=POST_HEADERS,
                timeout=30,
            )
            song_data = song_resp.json()
            songs.extend(song_data.get("songs") or [])
            if i + 200 < len(track_ids):
                time.sleep(0.3)

        tracks = []
        for song in songs:
            tracks.append({
                "id": str(song.get("id", "")),
                "name": song.get("name", ""),
                "artist": "/".join(a.get("name", "") for a in (song.get("ar") or [])),
                "album": (song.get("al") or {}).get("name", ""),
            })

        return {
            "playlist_name": playlist.get("name", ""),
            "track_count": playlist.get("trackCount", len(tracks)),
            "tracks": tracks,
        }
    except Exception:
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
        data = {
            "playlist_name": result.get("playlist_name", playlist_name),
            "track_count": result.get("track_count", len(result.get("tracks", []))),
            "tracks": result.get("tracks", []),
            "source": "网易云音乐实时数据",
        }
    else:
        data = _get_test_data(playlist_name)

    _write_cache(playlist_type, data)
    return data
