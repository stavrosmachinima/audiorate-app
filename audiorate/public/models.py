import hashlib

from sqlalchemy.sql import func

from audiorate.database import Column, PkModel, db


class Sample(PkModel):
    """
    Sample model representing an audio sample.
    """

    __tablename__ = "samples"

    id = Column(db.Integer, nullable=False, primary_key=True)
    audio_file = Column(db.String(100), nullable=False)
    transcript = Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Sample {self.audio_file}>"


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
    model = db.relationship("Model", backref="model_ratings")
    db.Index("idx_model_ratings_sample", "sample_id")

    __table_args__ = (
        db.UniqueConstraint(
            "session_id", "model_id", "sample_id", name="uq_session_model_sample"
        ),
    )

    def __repr__(self):
        """Represent instance as a string."""
        return f"<ModelRating(model_id={self.model_id}, sample_id={self.sample_id}, rating={self.rating})>"
