from datetime import datetime

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    avatar = db.Column(db.Text, nullable=True)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.Text, nullable=True)


class Admin_User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    admin = db.relationship('Admin', backref=db.backref('admin_user', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('admin_user', lazy='dynamic'))


class Premium(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('premiums', lazy='dynamic'))


class Admin_Premium(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    premium_id = db.Column(db.Integer, db.ForeignKey('premium.id'))
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())

    admin = db.relationship('Admin', backref=db.backref('admin_premium', lazy='dynamic'))
    premium = db.relationship('Premium', backref=db.backref('admin_premium', lazy='dynamic'))


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    card_name = db.Column(db.String(255), nullable=False)
    card_number_hash = db.Column(db.String(255), nullable=False, unique=True)
    month_hash = db.Column(db.String(255), nullable=False)
    year_hash = db.Column(db.String(255), nullable=False)
    cvv_hash = db.Column(db.String(255), nullable=False)


class User_Card(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'))

    user = db.relationship('User', backref=db.backref('user_card', lazy='dynamic'))
    card = db.relationship('Card', backref=db.backref('user_card', lazy='dynamic'))


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    duration = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    speed = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    image = db.Column(db.Text, nullable=False)
    type = db.Column(db.String, nullable=False)

    user = db.relationship('User', backref=db.backref('activities', lazy='dynamic'))
