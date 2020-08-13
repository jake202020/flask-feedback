from flask_sqlalchemy import flask_sqlalchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    """connect to database"""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User Model"""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                        primary_key = True)

    password = db.Column(db.Text,
                        nullable=False)

    email = db.Column(db.String(50),
                        nullable=False)

    first_name = db.Column(db.String(30),
                        nullable=False)

    last_name = db.Column(db.String(30),
                        nullable=False)