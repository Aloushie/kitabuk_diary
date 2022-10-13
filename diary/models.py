from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    entries = db.relationship('Quest')
    expert = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)

    questions_asked = db.relationship(
        'Question', 
        foreign_keys='Question.asked_by_id', 
        backref='asker', 
        lazy=True
    )
    
    answers_requested = db.relationship(
        'Question',
        foreign_keys='Question.expert_id',
        backref='expert',
        lazy=True
    )

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    asked_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    expert_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))