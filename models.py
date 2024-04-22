from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from werkzeug.security import check_password_hash

app = Flask(__name__)

app.config['SECRET_KEY']= 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/movie'

db = SQLAlchemy(app)
Migrate = Migrate(app, db)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    launching = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    ticket_price = db.Column(db.Integer, nullable=False)
    schedules = db.relationship('Schedule', back_populates='movie')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    movies = db.relationship('Movie', backref='info_category', lazy='dynamic')

class Theater(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room = db.Column(db.Integer, unique=True)
    total_seat = db.Column(db.Integer)
    schedules = db.relationship('Schedule', backref='info_theater', lazy='dynamic')

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    time = db.Column(db.Time, nullable=False) 
    movie = db.relationship('Movie', back_populates='schedules')
    transactions = db.relationship('Transaction', backref='info_schedule', lazy='dynamic')
    theater_id = db.Column(db.Integer, db.ForeignKey('theater.id'))

class Topup(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Integer, default=0)
    is_confirmed = db.Column(db.Boolean, default=False)
    
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)
    date = db.Column(db.Date, default=0)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    balance = db.Column(db.Integer, default=0)
    role = db.Column(db.String(20), default='user')
    transactions = db.relationship('Transaction', backref='info_user', lazy='dynamic')

    def admin_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            username = request.authorization.username
            user = User.query.filter_by(username=username).first()
            if user and user.role == "admin":
                return fn(*args, **kwargs)
            else:
                return jsonify({
                    "error": "Unauthorized"
                    }), 401
        return wrapper

    def admin_or_user_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            username = request.authorization.username
            password = request.authorization.password
            
            current_user = User.query.filter_by(username=username).first()

            if not current_user or not check_password_hash(current_user.password, password):
                return jsonify({"error": "Unauthorized"}), 401
            
            kwargs["current_user"] = current_user
            return fn(*args, **kwargs)
        
        return wrapper

