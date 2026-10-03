from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

import database as db
from config import GALLERY_ITEMS, LINK_DEFAULTS

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template(
        "index.html",
        active="home",
        diary_entries=db.list_diary(only_published=True, limit=3),
        gallery_items=GALLERY_ITEMS[:3],
    )


@main_bp.route("/profile")
def profile():
    return render_template("profile.html", active="profile")


@main_bp.route("/live")
def live():
    return render_template("live.html", active="live")


@main_bp.route("/playlist")
def playlist():
    return render_template("playlist.html", active="playlist")


@main_bp.route("/gallery")
def gallery():
    return render_template("gallery.html", active="gallery", items=GALLERY_ITEMS)


@main_bp.route("/links")
def links():
    return render_template("links.html", active="links", links=LINK_DEFAULTS)


@main_bp.route("/diary")
def diary():
    return render_template(
        "diary.html", active="diary", entries=db.list_diary(only_published=True)
    )


@main_bp.route("/diary/<int:entry_id>")
def diary_detail(entry_id):
    entry = db.get_diary(entry_id)
    if not entry or not entry.get("published"):
        abort(404)
    return render_template("diary_detail.html", active="diary", entry=entry)


@main_bp.route("/board", methods=["GET", "POST"])
def board():
    if request.method == "POST":
        nickname = (request.form.get("nickname") or "").strip()[:24]
        content = (request.form.get("content") or "").strip()[:500]
        if not content:
            flash("留言内容不能为空哦~", "error")
        else:
            db.create_message(nickname or "无名小鱼", content, approved=0)
            flash("留言已投进大海，等待闪闪审核后出现~", "success")
        return redirect(url_for("main.board"))

    return render_template(
        "board.html", active="board", messages=db.list_messages(approved=True)
    )
