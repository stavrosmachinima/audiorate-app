# -*- coding: utf-8 -*-
"""Helper utilities and decorators."""
import json
import os

from flask import current_app as app
from flask import flash


def flash_errors(form, category="warning"):
    """Flash all errors for a form."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{getattr(form, field).label.text} - {error}", category)


def load_audio_samples(file_name, convert_keys_to_int=True):
    """Load audio samples from the filesystem."""
    json_path = os.path.join(os.path.dirname(__file__), "data", file_name)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if convert_keys_to_int:
                return {int(k): v for k, v in data.items()}
            return data
    except FileNotFoundError:
        app.logger.error(f"File not found: {json_path}")
        return {}
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON decode error for {file_name}: {e}")
        return {}
    except Exception as e:
        app.logger.error(f"Unexpected error for {file_name}: {e}")
        return {}
