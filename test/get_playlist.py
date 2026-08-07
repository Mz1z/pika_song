# -*- coding: utf-8 -*-
"""
网易云音乐 PC 客户端(cloudmusic.dll v3.1.32.205206)歌单接口调用脚本

逆向分析结论 (基于 cloudmusic.dll 分析):
  1. PC 客户端为 CEF 混合架构, 业务逻辑 JS 打包在加密的 package/orpheus.ntpk 中
  2. 网络请求域名: interface.music.163.com / interfacepc.music.163.com
     (确认于 sub_180DA7840 域名配置表)
  3. PC 端请求使用 eapi 加密协议, 关键常量在 cloudmusic.dll 密钥表 (sub_180CB8A50):
     - AES-128-CBC key:  e82ckenh8dichen8
     - IV:               0102030405060708
     - 签名串格式:        nobody{path}use{data}md5forencrypt
     - 拼接格式:         {data}-36cd479b6b5-{path}-36cd479b6b5-{md5}
     - 输出:             AES 加密后转大写 HEX
  4. eapi 加密已实测验证正确 (POST /api/login/token/refresh 返回 {"code":301} 而非解密失败)
  5. 歌单详情接口实测:
     - GET  https://music.163.com/api/playlist/detail?id=...  仅返回前 10 条
     - POST https://music.163.com/api/v6/playlist/detail      返回全部 trackIds + 前10条详情
     - POST https://music.163.com/api/v3/song/detail          按 trackIds 批量获取歌曲完整信息
  本脚本采用方案: v6/playlist/detail 获取歌单全部 trackIds, 再调用 song/detail 批量获取歌曲信息。
"""

import hashlib
import json
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from Crypto.Cipher import AES

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/91.0.4472.164 "
                  "NeteaseMusicDesktop/3.1.32.205206",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://music.163.com/",
    "Origin": "https://music.163.com",
}


# ---------------------------------------------------------------------------
# eapi 加密 (逆向自 cloudmusic.dll 密钥表)
# ---------------------------------------------------------------------------
def eapi_encrypt(path: str, data: dict) -> str:
    """网易云 PC 端 eapi 加密, 返回 params 值 (大写 HEX)。

    path: 接口路径, 如 /api/v3/playlist/detail
    data: 请求参数 dict
    """
    text = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    message = "nobody" + path + "use" + text + "md5forencrypt"
    digest = hashlib.md5(message.encode("utf-8")).hexdigest()
    data2 = text + "-36cd479b6b5-" + path + "-36cd479b6b5-" + digest

    key = b"e82ckenh8dichen8"
    iv = b"0102030405060708"
    pad = 16 - len(data2.encode("utf-8")) % 16
    padded = data2.encode("utf-8") + bytes([pad]) * pad
    enc = AES.new(key, AES.MODE_CBC, iv).encrypt(padded)
    return enc.hex().upper()


def eapi_request(path: str, data: dict, host: str = "https://interface.music.163.com",
                 timeout: int = 30) -> requests.Response:
    """通过 eapi 加密协议调用 PC 端接口 (备用方案)。"""
    params = eapi_encrypt(path, data)
    return requests.post(host + path, data={"params": params},
                         headers=DEFAULT_HEADERS, timeout=timeout)


# ---------------------------------------------------------------------------
# 方案A: 网页版接口 (已实测可用)
# ---------------------------------------------------------------------------
def get_playlist_track_ids(playlist_id: str) -> tuple:
    """POST /api/v6/playlist/detail 获取歌单全部 trackIds。

    返回: (playlist_meta, track_ids)
    """
    url = "https://music.163.com/api/v6/playlist/detail"
    data = {"id": str(playlist_id), "n": "100000", "s": "8"}
    r = requests.post(url, data=data, headers=DEFAULT_HEADERS, timeout=30)
    j = r.json()
    if j.get("code") != 200 or not j.get("playlist"):
        raise RuntimeError(f"获取歌单信息失败: {j}")
    pl = j["playlist"]
    ids = [t["id"] for t in (pl.get("trackIds") or [])]
    return pl, ids


def get_songs_batch(song_ids: list, batch_size: int = 200) -> list:
    """POST /api/v3/song/detail 按 ID 批量获取歌曲完整信息。"""
    url = "https://music.163.com/api/v3/song/detail"
    songs = []
    for i in range(0, len(song_ids), batch_size):
        batch = song_ids[i:i + batch_size]
        c = json.dumps([{"id": sid} for sid in batch])
        r = requests.post(url, data={"c": c, "ids": json.dumps(batch)},
                          headers=DEFAULT_HEADERS, timeout=30)
        j = r.json()
        songs.extend(j.get("songs") or [])
        if i + batch_size < len(song_ids):
            time.sleep(0.3)
    return songs


# ---------------------------------------------------------------------------
# 方案B: eapi 加密接口 (PC 客户端真实协议, 路径参数因版本可能需调整)
# ---------------------------------------------------------------------------
def get_playlist_via_eapi(playlist_id: str) -> dict:
    """通过 PC 端 eapi 协议获取歌单详情 (备用)。"""
    path = "/api/v3/playlist/detail"
    data = {"id": str(playlist_id), "n": 100000, "s": 8}
    r = eapi_request(path, data)
    return r.json()


# ---------------------------------------------------------------------------
def main():
    playlist_id = sys.argv[1] if len(sys.argv) > 1 else "17849227734"

    print(f"正在获取歌单 {playlist_id} ...")
    pl, ids = get_playlist_track_ids(playlist_id)
    print(f"歌单: {pl.get('name')}")
    print(f"歌曲总数: {pl.get('trackCount')} / trackIds: {len(ids)}")

    if not ids:
        print("歌单为空")
        return

    print("正在批量获取歌曲详情 ...")
    songs = get_songs_batch(ids)

    print(f"\n共获取 {len(songs)} 首歌曲:\n")
    print(f"{'序号':<4}{'ID':<14}{'歌名':<40}{'歌手':<40}{'专辑'}")
    print("-" * 120)
    for idx, s in enumerate(songs, 1):
        name = s.get("name", "")
        artists = "/".join(a.get("name", "") for a in (s.get("ar") or []))
        album = (s.get("al") or {}).get("name", "")
        print(f"{idx:<4}{s.get('id', ''):<14}{name:<40}{artists:<40}{album}")

    # 保存完整 JSON
    out_file = f"playlist_{playlist_id}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({"playlist": pl, "songs": songs}, f, ensure_ascii=False, indent=2)
    print(f"\n完整数据已保存到 {out_file}")


if __name__ == "__main__":
    main()
