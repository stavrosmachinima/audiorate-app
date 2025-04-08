# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint
from flask import current_app as app
from flask import flash, redirect, render_template, request, url_for

from audiorate.extensions import db
from audiorate.public.forms import RatingForm
from audiorate.public.models import Model, ModelRating, RatingSession, Sample
from audiorate.utils import load_audio_samples

blueprint = Blueprint("public", __name__, static_folder="../static")
MODEL_COUNT = len(load_audio_samples("models.json", convert_keys_to_int=True))
AUDIO_SAMPLES = load_audio_samples("samples.json", convert_keys_to_int=True)


@blueprint.route("/", methods=["GET"])
def home():
    """Home page."""
    form = RatingForm()
    return render_template("public/home.html", form=form, audio_samples=AUDIO_SAMPLES)


@blueprint.route("/thank_you", methods=["GET"])
def thank_you():
    """Thank you page."""
    return render_template("public/thank_you.html")


@blueprint.route("/submit_rating", methods=["POST"])
def submit_rating():
    """Submit a rating."""
    app.logger.info("Rating submission started.")
    form = RatingForm(request.form)
    if form.validate_on_submit():
        all_ratings_filled = all(
            float(rating_form.rating.data) >= 0.5 for rating_form in form.ratings
        )
        if not all_ratings_filled:
            app.logger.warning("Not all ratings were filled. Submission aborted.")
            flash("Please complete all ratings before submitting.", "error")
            return render_template("public/home.html", form=form, audio_samples=AUDIO_SAMPLES)  # Keep filled values

        try:
            sample_count = Sample.query.count()
            model_count = Model.query.count()
            if sample_count == 0 or model_count < MODEL_COUNT:
                app.logger.error(
                    "Database not properly initialized. Sample or model count is insufficient."
                )
                flash(
                    "Database not properly initialized. Please contact administrator.",
                    "error",
                )
                return render_template("public/home.html", form=form, audio_samples=AUDIO_SAMPLES)

            session = RatingSession(
                session_hash=RatingSession.create_session(
                    request.user_agent.string, ip_address=request.remote_addr
                ),
                user_agent=request.user_agent.string,
                ip_address=request.remote_addr,
            )
            db.session.add(session)
            db.session.flush()
            app.logger.info(
                f"Session created with ID {session.id} and hash {session.session_hash}"
            )

            samples = {}
            models = {}
            ratings_data = []

            for i, rating_form in enumerate(form.ratings):
                sample_index = (i // MODEL_COUNT) + 1
                model_index = (i % MODEL_COUNT) + 1

                if sample_index not in samples:
                    sample = Sample.query.filter_by(id=sample_index).first()
                    if not sample:
                        app.logger.error(
                            f"Sample {sample_index} not found in database."
                        )
                        flash(
                            f"Sample {sample_index} not found. Please contact administrator.",
                            "error",
                        )
                        return render_template("public/home.html", form=form, audio_samples=AUDIO_SAMPLES)
                    samples[sample_index] = sample

                if model_index not in models:
                    model = Model.query.filter_by(id=model_index).first()
                    if not model:
                        app.logger.error(f"Model {model_index} not found in database.")
                        flash(
                            f"Model {model_index} not found. Please contact administrator.",
                            "error",
                        )
                        return render_template("public/home.html", form=form, audio_samples=AUDIO_SAMPLES)
                    models[model_index] = model

                ratings_data.append(
                    {
                        "sample_id": samples[sample_index].id,
                        "model_id": models[model_index].id,
                        "rating": float(rating_form.rating.data),
                    }
                )

                added_combinations = set()
            for rating_item in ratings_data:
                combo_key = (
                    session.id,
                    rating_item["sample_id"],
                    rating_item["model_id"],
                )
                if combo_key in added_combinations:
                    app.logger.warning(
                        f"Duplicate rating submission detected for session {session.id}, sample {rating_item['sample_id']}, model {rating_item['model_id']}. Skipping."
                    )
                    continue
                added_combinations.add(combo_key)
                model_rating = ModelRating(
                    session_id=session.id,
                    model_id=rating_item["model_id"],
                    sample_id=rating_item["sample_id"],
                    rating=rating_item["rating"],
                )
                db.session.add(model_rating)
            db.session.commit()
            rating_summary = {
                "session_id": session.id,
                "ratings": [
                    {
                        "sample_id": samples[(i // MODEL_COUNT) + 1].id,
                        "model_id": models[(i % MODEL_COUNT) + 1].id,
                        "rating": float(rating_form.rating.data),
                    }
                    for i, rating_form in enumerate(form.ratings)
                    if (i // MODEL_COUNT) + 1 in samples
                    and (i % MODEL_COUNT) + 1 in models
                ],
            }

            app.logger.info(f"Rating submission completed. Summary: {rating_summary}")
            return redirect(url_for("public.thank_you"))
        except Exception as e:
            db.session.rollback()
            app.logger.error(
                f"Error during rating submission: {str(e)}. Rolling back session.",
                exc_info=True,
            )
            flash(
                "An error occurred while submitting your rating. Please try again.",
                "error",
            )
    else:
        app.logger.warning(
            f"Rating form validation failed: {form.errors}. Submission aborted."
        )
        flash("Invalid rating, please check your inputs.", "error")
        return render_template("public/home.html", form=form, audio_samples=AUDIO_SAMPLES)  # Keep existing values
