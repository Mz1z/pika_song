from flask import Flask

import database as db
from config import (
    BILIBILI_LIVE,
    BILIBILI_SPACE,
    LINK_DEFAULTS,
    SECRET_KEY,
    SITE_DESCRIPTION,
    SITE_NAME,
    SITE_SUBTITLE,
)
from routes.admin import admin_bp
from routes.api import api_bp
from routes.main import main_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    db.init_db()

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_globals():
        return {
            "site": {
                "name": SITE_NAME,
                "subtitle": SITE_SUBTITLE,
                "description": SITE_DESCRIPTION,
                "space": BILIBILI_SPACE,
                "live": BILIBILI_LIVE,
            },
            "profile": db.get_profile(),
            "links": LINK_DEFAULTS,
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
