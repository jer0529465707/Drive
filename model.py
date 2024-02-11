from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import datetime as dt

db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100))

    is_admin_user = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def set_admin(self):
        self.is_admin_user = True

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    file_size = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=dt.datetime.utcnow)


class FileShare(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    shared_at = db.Column(db.DateTime, default=dt.datetime.utcnow)

    file = db.relationship(
        "File", backref=db.backref("file_shares", cascade="all, delete-orphan")
    )
    user = db.relationship(
        "User", backref=db.backref("file_shares", cascade="all, delete-orphan")
    )
