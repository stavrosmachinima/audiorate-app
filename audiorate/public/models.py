import hashlib

from sqlalchemy.sql import func

from audiorate.database import Column, PkModel, db


class Sample(PkModel):
    """
    Sample model representing an audio sample.
    """

    __tablename__ = "samples"

    id = Column(db.Integer, nullable=False, primary_key=True)

    model_id = Column(db.Integer, db.ForeignKey("models.id"), nullable=True)
    ground_truth_id = Column(
        db.Integer, db.ForeignKey("samples.id", ondelete="CASCADE"), nullable=True
    )
    is_ground_truth = Column(db.Boolean, nullable=False, default=False)
    filename = Column(db.String(100), nullable=False)
    filepath = Column(db.String(255), nullable=False)
    text = Column(db.Text, nullable=False)

    model = db.relationship(
        "Model", backref=db.backref("samples", cascade="all, delete")
    )
    variants = db.relationship(
        "Sample",
        backref=db.backref("ground_truth", remote_side=[id]),
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        if self.is_ground_truth:
            return f"<Sample {self.id} (Ground Truth)>"
        return f"<Sample {self.filename} (Model: {self.model_name if self.model else 'None'})>"


class Model(PkModel):
    __tablename__ = "models"

    id = Column(db.Integer, nullable=False, primary_key=True)
    name = Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<Model {self.name}>"


class RatingSession(PkModel):
    __tablename__ = "rating_sessions"

    id = Column(db.Integer, nullable=False, primary_key=True)
    session_hash = Column(db.String(64), nullable=False, index=True)
    user_agent = Column(db.String(255), nullable=True)
    ip_address = Column(db.String(45), nullable=True)
    created_at = Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
    )

    def __repr__(self):
        return f"<RatingSession {self.created_at}>"

    @classmethod
    def create_session(cls, user_agent: str, ip_address: str):
        """
        Generate a consistent hash from IP and user agent
        """
        combined = f"{user_agent}{ip_address}"
        return hashlib.sha256(combined.encode()).hexdigest()[:64]


class ModelRating(PkModel):
    __tablename__ = "model_ratings"

    id = Column(db.Integer, primary_key=True)
    session_id = Column(db.Integer, db.ForeignKey("rating_sessions.id"), nullable=False)
    model_id = Column(db.Integer, db.ForeignKey("models.id"), nullable=False)
    sample_id = Column(db.Integer, db.ForeignKey("samples.id"), nullable=False)
    rating = Column(db.Float, nullable=False)
    created_at = Column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
    )

    session = db.relationship(
        "RatingSession", backref=db.backref("model_ratings", cascade="all, delete")
    )
    sample = db.relationship("Sample", backref="model_ratings")

    __table_args__ = (
        db.UniqueConstraint(
            "session_id", "model_id", "sample_id", name="uq_session_model_sample"
        ),
    )

    def __repr__(self):
        """Represent instance as a string."""
        return f"<ModelRating(model_id={self.model_id}, sample_id={self.sample_id}, rating={self.rating})>"
