# -*- coding: utf-8 -*-
"""Public section, including homepage and signup."""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from audiorate.public.forms import RatingForm

blueprint = Blueprint("public", __name__, static_folder="../static")


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
        # Process the rating here
        rating = [float(rating_form.rating.data) for rating_form in form.ratings]
        flash(f"Rating submitted: {rating}", "success")
        return redirect(url_for("public.thank_you"))
    print(form.errors)
    flash("Invalid rating, please check your inputs.", "error")
    return render_template("public/home.html", form=form)  # Keep existing values
