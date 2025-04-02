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


@blueprint.route("/submit_rating", methods=["POST"])
def submit_rating():
    """Submit a rating."""
    form = RatingForm(request.form)
    if form.validate_on_submit():
        # Process the rating here
        rating = form.rating.data
        flash(f"Rating submitted: {rating}", "success")
    else:
        flash("Invalid rating", "error")
    return redirect(url_for("public/home.html"))
