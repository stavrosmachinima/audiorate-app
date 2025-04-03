# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from audiorate.extensions import db
from audiorate.public.forms import RatingForm
from audiorate.public.models import Model, ModelRating, RatingSession, Sample

blueprint = Blueprint("public", __name__, static_folder="../static")
MODEL_COUNT = 3


@blueprint.route("/", methods=["GET"])
def home():
    """Home page."""
    form = RatingForm()
    return render_template("public/home.html", form=form)


@blueprint.route("/thank_you", methods=["GET"])
def thank_you():
    """Thank you page."""
    return render_template("public/thank_you.html")


@blueprint.route("/submit_rating", methods=["POST"])
def submit_rating():
    """Submit a rating."""
    print(request.form)
    form = RatingForm(request.form)
    if form.validate_on_submit():
        all_ratings_filled = all(
            float(rating_form.rating.data) >= 0.5 for rating_form in form.ratings
        )
        if not all_ratings_filled:
            flash("Please complete all ratings before submitting.", "error")
            return render_template("public/home.html", form=form)  # Keep filled values

        sample_count = Sample.query.count()
        model_count = Model.query.count()
        if sample_count == 0 or model_count < MODEL_COUNT:
            flash(
                "Database not properly initialized. Please contact administrator.",
                "error",
            )
            return render_template("public/home.html", form=form)

        session = RatingSession(
            session_hash=RatingSession.create_session(
                request.user_agent.string, ip_address=request.remote_addr
            ),
            user_agent=request.user_agent.string,
            ip_address=request.remote_addr,
        )
        db.session.add(session)
        db.session.flush()

        samples = {}
        models = {}
        ratings_data = []

        for i, rating_form in enumerate(form.ratings):
            sample_index = (i // MODEL_COUNT) + 1
            model_index = (i % MODEL_COUNT) + 1
            print(f"Sample index: {sample_index}, Model index: {model_index}")

            if sample_index not in samples:
                sample = Sample.query.filter_by(id=sample_index).first()
                if not sample:
                    flash(
                        f"Sample {sample_index} not found. Please contact administrator.",
                        "error",
                    )
                    return render_template("public/home.html", form=form)
                samples[sample_index] = sample

            if model_index not in models:
                model = Model.query.filter_by(id=model_index).first()
                if not model:
                    flash(
                        f"Model {model_index} not found. Please contact administrator.",
                        "error",
                    )
                    return render_template("public/home.html", form=form)
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
                print(f"Duplicate combination found: {combo_key}")
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
                if (i // MODEL_COUNT) + 1 in samples and (i % MODEL_COUNT) + 1 in models
            ],
        }

        print(f"Rating submitted: {rating_summary}")
        return redirect(url_for("public.thank_you"))
    print(form.errors)
    flash("Invalid rating, please check your inputs.", "error")
    return render_template("public/home.html", form=form)  # Keep existing values
