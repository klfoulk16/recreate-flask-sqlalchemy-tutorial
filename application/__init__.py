"""Flask App Factory"""

import os
from flask import Flask, render_template, request
from application.flask_sqlalchemy import Flask_SQLAlchemy

db = Flask_SQLAlchemy()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    # configuration and database location
    app.config.from_mapping(
        SECRET_KEY="dev",
        # change string if on Windows
        DATABASE=f"sqlite:////{os.path.join(app.instance_path, 'application.db')}",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # tell the database where to find the models
    from application.database import User
    # Initialize SQLAlchemy ORM
    db.init_app(app)

    from application.api import create_user
    # a simple page that allows us to register and then says hello
    @app.route("/", methods=("GET", "POST"))
    def hello():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            create_user(username, password)
            return "Hello World"
        else:
            return render_template("register.html", users=None)

    return app
