from shop import db
from flask_login import UserMixin


# Define User DataModel
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile = db.Column(db.String(200), nullable=False, default='profile.jpg')

    def __repr__(self):
        return '<User %r>' % self.username

