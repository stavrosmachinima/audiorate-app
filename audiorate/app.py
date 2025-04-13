# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
import logging
import os
import sys
import time
from datetime import timedelta
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template
from flask_session import Session

from audiorate import commands, public
from audiorate.extensions import (
    cache,
    csrf_protect,
    db,
    debug_toolbar,
    flask_static_digest,
    migrate,
)


def create_app(config_object="audiorate.settings"):
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config_object)
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_PERMANENT"] = True
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=5)
    app.config["SESSION_FILE_DIR"] = "/app/data/sessions"
    app.config["SQLALCHEMY_RECORD_QUERIES"] = True
    app.config["VERSION"] = str(int(time.time()))
    os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)
    Session(app)
    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)
    configure_logger(app)

    # Pass config to templates
    @app.context_processor
    def inject_config():
        return dict(config=app.config)

    @app.after_request
    def add_cache_control(response):
        if (
            "text/css" in response.content_type
            or "application/javascript" in response.content_type
        ):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    return app


def register_extensions(app):
    """Register Flask extensions."""
    cache.init_app(app)
    db.init_app(app)
    csrf_protect.init_app(app)
    debug_toolbar.init_app(app)
    migrate.init_app(app, db)
    flask_static_digest.init_app(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(public.views.blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""

    def render_error(error):
        """Render error template."""
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, "code", 500)
        return render_template(f"{error_code}.html"), error_code

    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {"db": db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.seed)


def configure_logger(app):
    """Configure loggers."""
    log_level = app.config.get("LOG_LEVEL", "INFO").upper()
    if log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        log_level = "INFO"
    app.logger.info(f"Log level set to {log_level}")
    formatter = logging.Formatter(
        "%(asctime)s  - %(levelname)s - %(module)s - %(message)s"
    )
    logs_dir = os.path.join(os.path.dirname(app.root_path), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, "audiorate.log"),
        encoding="utf-8",
        backupCount=10,
        maxBytes=1024 * 1024 * 10,
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(getattr(logging, log_level))

    error_file_handler = RotatingFileHandler(
        os.path.join(logs_dir, "errors.log"),
        encoding="utf-8",
        backupCount=10,
        maxBytes=1024 * 1024 * 10,
    )
    error_file_handler.setFormatter(formatter)
    error_file_handler.setLevel(logging.ERROR)

    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    if app.debug:
        app.logger.debug(f"Debug mode is {'on' if app.debug else 'off'}")
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(stream_handler)
    app.logger.setLevel(getattr(logging, log_level))

    if app.debug:
        logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

    app.logger.info("Logger initialized")
