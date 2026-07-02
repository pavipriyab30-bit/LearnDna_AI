from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    learning_style = db.Column(db.String(50))

    difficulty = db.Column(db.String(30))

    language = db.Column(db.String(30))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    history = db.relationship(
        "LearningHistory",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class LearningHistory(db.Model):
    __tablename__ = "learning_history"

    id = db.Column(db.Integer, primary_key=True)

    topic = db.Column(db.String(200), nullable=False)

    explanation = db.Column(db.Text, nullable=False)

    quiz = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )