import flask
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Student(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password, password)


class Course(db.Model):
    courseID = db.Column(db.String(100), primary_key=True, unique=True)
    title = db.Column(db.String(100))
    description = db.Column(db.String(225))
    credits  = db.Column(db.Integer)
    term = db.Column(db.String(25))


class Enrollment(db.Model):
    user_id = db.Column(db.Integer,  primary_key=True)
    courseID = db.Column(db.String(10))