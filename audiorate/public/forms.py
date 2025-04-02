from flask_wtf import FlaskForm
from wtforms import HiddenField, RadioField
from wtforms.validators import DataRequired


class RatingForm(FlaskForm):
    csrf_token = HiddenField()
    rating = RadioField(
        "Rating",
        choices=[
            (5.0, "5 - Excellent"),
            (4.5, "4.5"),
            (4.0, "4 - Good"),
            (3.5, "3.5"),
            (3.0, "3 - Fair"),
            (2.5, "2.5"),
            (2.0, "2 - Poor"),
            (1.5, "1.5"),
            (1.0, "1 - Bad"),
            (0.5, "0.5"),
        ],
        validators=[DataRequired()],
    )

    def __init__(self, *args, **kwargs):
        super(RatingForm, self).__init__(*args, **kwargs)
        self.rating.description = "Rate the audio quality from 0.5 to 5"
        print("KAPPA")
