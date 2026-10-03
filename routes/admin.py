import hmac
from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

import database as db
from config import ADMIN_PASSWORD

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if hmac.compare_digest(password, ADMIN_PASSWORD):
            session["admin_logged_in"] = True
            nxt = request.args.get("next") or url_for("admin.dashboard")
            return redirect(nxt)
        flash("密码不对，再试一次吧~", "error")
    return render_template("admin/login.html")


@admin_bp.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("已退出后台", "success")
    return redirect(url_for("admin.login"))


@admin_bp.route("/")
@login_required
def dashboard():
    return render_template(
        "admin/dashboard.html", stats=db.stats(), entries=db.list_diary(limit=5)
    )


@admin_bp.route("/diary")
@login_required
def diary_list():
    return render_template("admin/diary_list.html", entries=db.list_diary())


@admin_bp.route("/diary/new", methods=["GET", "POST"])
@login_required
def diary_new():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        content = (request.form.get("content") or "").strip()
        mood = (request.form.get("mood") or "").strip()
        published = 1 if request.form.get("published") else 0
        if not title or not content:
            flash("标题和内容都不能为空", "error")
        else:
            db.create_diary(title, content, mood, published)
            flash("小鱼日志已保存", "success")
            return redirect(url_for("admin.diary_list"))
    return render_template("admin/diary_edit.html", entry=None)


@admin_bp.route("/diary/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def diary_edit(entry_id):
    entry = db.get_diary(entry_id)
    if not entry:
        flash("这条日志不存在", "error")
        return redirect(url_for("admin.diary_list"))
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        content = (request.form.get("content") or "").strip()
        mood = (request.form.get("mood") or "").strip()
        published = 1 if request.form.get("published") else 0
        if not title or not content:
            flash("标题和内容都不能为空", "error")
        else:
            db.update_diary(entry_id, title, content, mood, published)
            flash("小鱼日志已更新", "success")
            return redirect(url_for("admin.diary_list"))
    return render_template("admin/diary_edit.html", entry=entry)


@admin_bp.route("/diary/<int:entry_id>/delete", methods=["POST"])
@login_required
def diary_delete(entry_id):
    db.delete_diary(entry_id)
    flash("日志已删除", "success")
    return redirect(url_for("admin.diary_list"))


@admin_bp.route("/messages")
@login_required
def messages():
    return render_template(
        "admin/messages.html",
        pending=db.list_messages(approved=False),
        approved=db.list_messages(approved=True),
    )


@admin_bp.route("/messages/<int:message_id>/approve", methods=["POST"])
@login_required
def message_approve(message_id):
    db.approve_message(message_id)
    flash("留言已通过审核", "success")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/messages/<int:message_id>/delete", methods=["POST"])
@login_required
def message_delete(message_id):
    db.delete_message(message_id)
    flash("留言已删除", "success")
    return redirect(url_for("admin.messages"))


@admin_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_data = db.get_profile()
    if request.method == "POST":
        fields = [
            "name",
            "en_name",
            "slogan",
            "birthday",
            "height",
            "debut_date",
            "constellation",
            "blood_type",
            "hobby",
            "skills",
            "tags",
            "intro",
            "room_name",
            "room_notice",
            "room_schedule",
        ]
        db.update_profile({field: request.form.get(field, "") for field in fields})
        flash("基本资料已更新", "success")
        return redirect(url_for("admin.profile"))
    return render_template("admin/profile.html", profile=profile_data)
