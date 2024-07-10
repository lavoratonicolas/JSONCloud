from flask import Flask, render_template
from flask_bcrypt import Bcrypt
from .database import *
from .routes import routes_blueprint
from .extension import bcrypt


def create_app():
    app = Flask(__name__)
    bcrypt.init_app(app)
    routes_blueprint(app)

    @app.get("/")
    def home():
        return render_template("index.html")

    return app
