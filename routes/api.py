from flask import Blueprint, abort, jsonify, request

from live import get_live_status
from netease import get_playlist

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/playlist/<playlist_type>")
def api_playlist(playlist_type):
    if playlist_type not in ("learning", "skilled"):
        abort(404)
    force_refresh = request.args.get("refresh", "").lower() == "true"
    return jsonify(get_playlist(playlist_type, force_refresh=force_refresh))


@api_bp.route("/live")
def api_live():
    force_refresh = request.args.get("refresh", "").lower() == "true"
    return jsonify(get_live_status(force_refresh=force_refresh))
