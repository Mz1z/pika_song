import os
import sqlite3
from datetime import datetime

from config import DB_PATH, GALLERY_ITEMS, PROFILE_DEFAULTS

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS profile (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS diary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                mood TEXT DEFAULT '',
                published INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                content TEXT NOT NULL,
                approved INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                emoji TEXT DEFAULT '🖼️',
                image TEXT DEFAULT '',
                gradient TEXT DEFAULT 'linear-gradient(135deg,#0077b6,#48cae4)',
                sort_order INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            );
            """
        )
        for key, value in PROFILE_DEFAULTS.items():
            conn.execute(
                "INSERT OR IGNORE INTO profile (key, value) VALUES (?, ?)",
                (key, value),
            )
        if conn.execute("SELECT COUNT(*) AS c FROM gallery").fetchone()["c"] == 0:
            for index, item in enumerate(GALLERY_ITEMS):
                conn.execute(
                    "INSERT INTO gallery (title, description, emoji, image, gradient, sort_order, created_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        item.get("title", ""),
                        item.get("desc", ""),
                        item.get("emoji", "🖼️"),
                        "",
                        item.get("gradient", ""),
                        index,
                        _now(),
                    ),
                )
        conn.commit()
    finally:
        conn.close()


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ----------------------------- profile -----------------------------

def get_profile():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT key, value FROM profile").fetchall()
        data = dict(PROFILE_DEFAULTS)
        data.update({row["key"]: row["value"] for row in rows})
        return data
    finally:
        conn.close()


def update_profile(values):
    conn = get_conn()
    try:
        for key, value in values.items():
            conn.execute(
                "INSERT INTO profile (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value or ""),
            )
        conn.commit()
    finally:
        conn.close()


# ----------------------------- diary -----------------------------

def list_diary(only_published=False, limit=None):
    conn = get_conn()
    try:
        sql = "SELECT * FROM diary"
        params = []
        if only_published:
            sql += " WHERE published = 1"
        sql += " ORDER BY created_at DESC, id DESC"
        if limit:
            sql += " LIMIT ?"
            params.append(limit)
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def get_diary(entry_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM diary WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_diary(title, content, mood="", published=1):
    conn = get_conn()
    try:
        now = _now()
        cur = conn.execute(
            "INSERT INTO diary (title, content, mood, published, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (title, content, mood, published, now, now),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_diary(entry_id, title, content, mood="", published=1):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE diary SET title = ?, content = ?, mood = ?, published = ?, updated_at = ? "
            "WHERE id = ?",
            (title, content, mood, published, _now(), entry_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_diary(entry_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM diary WHERE id = ?", (entry_id,))
        conn.commit()
    finally:
        conn.close()


# ----------------------------- messages -----------------------------

def list_messages(approved=None):
    conn = get_conn()
    try:
        sql = "SELECT * FROM messages"
        params = []
        if approved is not None:
            sql += " WHERE approved = ?"
            params.append(1 if approved else 0)
        sql += " ORDER BY created_at DESC, id DESC"
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def create_message(nickname, content, approved=0):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO messages (nickname, content, approved, created_at) VALUES (?, ?, ?, ?)",
            (nickname, content, approved, _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def approve_message(message_id):
    conn = get_conn()
    try:
        conn.execute("UPDATE messages SET approved = 1 WHERE id = ?", (message_id,))
        conn.commit()
    finally:
        conn.close()


def delete_message(message_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
    finally:
        conn.close()


# ----------------------------- gallery -----------------------------

def list_gallery():
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT * FROM gallery ORDER BY sort_order ASC, id ASC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_gallery(item_id):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM gallery WHERE id = ?", (item_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def create_gallery(title, description="", emoji="🖼️", image="", gradient="", sort_order=0):
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO gallery (title, description, emoji, image, gradient, sort_order, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, emoji, image, gradient, sort_order, _now()),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_gallery(item_id, title, description="", emoji="🖼️", image="", gradient="", sort_order=0):
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE gallery SET title = ?, description = ?, emoji = ?, image = ?, "
            "gradient = ?, sort_order = ? WHERE id = ?",
            (title, description, emoji, image, gradient, sort_order, item_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_gallery(item_id):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM gallery WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()


def stats():
    conn = get_conn()
    try:
        diary_count = conn.execute("SELECT COUNT(*) AS c FROM diary").fetchone()["c"]
        msg_total = conn.execute("SELECT COUNT(*) AS c FROM messages").fetchone()["c"]
        msg_pending = conn.execute(
            "SELECT COUNT(*) AS c FROM messages WHERE approved = 0"
        ).fetchone()["c"]
        gallery_count = conn.execute("SELECT COUNT(*) AS c FROM gallery").fetchone()["c"]
        return {
            "diary_count": diary_count,
            "message_total": msg_total,
            "message_pending": msg_pending,
            "gallery_count": gallery_count,
        }
    finally:
        conn.close()
