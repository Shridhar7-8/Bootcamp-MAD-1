from flask_sqlalchemy import SQLAlchemy # Import SQLAlchemy from flask_sqlalchemy


db = SQLAlchemy()  # Create an instance of SQLAlchemy class


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False,unique=True)
    email = db.Column(db.String(40),nullable=False,unique=True)
    password = db.Column(db.String(100), nullable=False)
    post = db.relationship("Post", backref="user",lazy=True)

class Post(db.Model):
    __tablename__ = "posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    flagged = db.Column(db.Boolean, default=False)




