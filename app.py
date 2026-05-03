from flask import Flask, jsonify, render_template, request
from netease import get_playlist

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/playlist/learning")
def api_learning():
    force_refresh = request.args.get("refresh", "").lower() == "true"
    data = get_playlist("learning", force_refresh=force_refresh)
    return jsonify(data)


@app.route("/api/playlist/skilled")
def api_skilled():
    force_refresh = request.args.get("refresh", "").lower() == "true"
    data = get_playlist("skilled", force_refresh=force_refresh)
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
