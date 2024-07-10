from .users_routes import users_bp


def routes_blueprint(app):
    app.register_blueprint(users_bp, url_prexi="/api/users")
