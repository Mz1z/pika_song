import hmac
import os
import uuid
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
from config import ADMIN_PASSWORD, ALLOWED_IMAGE_EXT, UPLOAD_DIR

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def _save_gallery_image(file_storage):
    if not file_storage or not file_storage.filename:
        return ""
    ext = os.path.splitext(file_storage.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXT:
        return None
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{ext}"
    file_storage.save(os.path.join(UPLOAD_DIR, filename))
    return f"/static/uploads/gallery/{filename}"


def _gallery_form_data():
    title = (request.form.get("title") or "").strip()
    if not title:
        return None, "标题不能为空"

    description = (request.form.get("description") or "").strip()
    emoji = (request.form.get("emoji") or "🖼️").strip() or "🖼️"
    gradient = (request.form.get("gradient") or "").strip()
    try:
        sort_order = int((request.form.get("sort_order") or "0").strip())
    except ValueError:
        sort_order = 0

    image = (request.form.get("image") or "").strip()
    upload = request.files.get("image_file")
    if upload and upload.filename:
        saved = _save_gallery_image(upload)
        if saved is None:
            return None, "图片格式仅支持 png / jpg / jpeg / gif / webp"
        image = saved

    return {
        "title": title,
        "description": description,
        "emoji": emoji,
        "image": image,
        "gradient": gradient,
        "sort_order": sort_order,
    }, None


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


@admin_bp.route("/gallery")
@login_required
def gallery_list():
    return render_template("admin/gallery_list.html", items=db.list_gallery())


@admin_bp.route("/gallery/new", methods=["GET", "POST"])
@login_required
def gallery_new():
    if request.method == "POST":
        data, error = _gallery_form_data()
        if error:
            flash(error, "error")
        else:
            db.create_gallery(**data)
            flash("相册内容已添加", "success")
            return redirect(url_for("admin.gallery_list"))
    return render_template("admin/gallery_edit.html", item=None)


@admin_bp.route("/gallery/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def gallery_edit(item_id):
    item = db.get_gallery(item_id)
    if not item:
        flash("这条相册内容不存在", "error")
        return redirect(url_for("admin.gallery_list"))
    if request.method == "POST":
        data, error = _gallery_form_data()
        if error:
            flash(error, "error")
        else:
            db.update_gallery(item_id, **data)
            flash("相册内容已更新", "success")
            return redirect(url_for("admin.gallery_list"))
    return render_template("admin/gallery_edit.html", item=item)


@admin_bp.route("/gallery/<int:item_id>/delete", methods=["POST"])
@login_required
def gallery_delete(item_id):
    db.delete_gallery(item_id)
    flash("相册内容已删除", "success")
    return redirect(url_for("admin.gallery_list"))


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
