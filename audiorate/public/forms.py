from flask_wtf import FlaskForm
from wtforms import FieldList, FloatField, FormField, HiddenField
from wtforms.validators import DataRequired, NumberRange


class SingleRatingForm(FlaskForm):
    """Form for a single rating."""

    rating = FloatField(validators=[NumberRange(min=0, max=10)])


class RatingForm(FlaskForm):
    """Form for multiple ratings."""

    csrf_token = HiddenField()
    ratings = FieldList(FormField(SingleRatingForm), min_entries=1)
