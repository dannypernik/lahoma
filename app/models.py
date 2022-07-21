from datetime import datetime
from time import time
from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(32), index=True)
    last_name = db.Column(db.String(32), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(24), default = "unverified", index=True)
    notes = db.Column(db.String(500))

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_email_verification_token(self, expires_in=3600):
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_email_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_email']
        except:
            return
        return User.query.get(id)


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), unique=True, index=True)
    phone = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    status = db.Column(db.String(24), default = "active", index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'))

    def __repr__(self):
        return '<Client {}>'.format(self.first_name + " " + self.last_name)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(64), index=True)
    is_admin = db.Column(db.Boolean)
    status = db.Column(db.String(24), default = "active", index=True)
    clients = db.relationship('Client', backref='teacher', lazy='dynamic')

    def __repr__(self):
        return '<Teacher {}>'.format(self.first_name + " " + self.last_name)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
