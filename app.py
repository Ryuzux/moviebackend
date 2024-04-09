from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from functools import wraps
from flask_httpauth import HTTPBasicAuth
from datetime import date


app = Flask(__name__)

app.config['SECRET_KEY']= 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/movie'

db = SQLAlchemy(app)
Migrate = Migrate(app, db)
auth = HTTPBasicAuth()

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    launching = db.Column(db.Date, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    ticket_price = db.Column(db.Integer, nullable=False)
    schedules = db.relationship('Schedule', backref='info_movie', lazy='dynamic')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    movies = db.relationship('Movie', backref='info_category', lazy='dynamic')

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    time = db.Column(db.Time, nullable=False)
    transactions = db.relationship('Transaction', backref='info_schedule', lazy='dynamic')

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
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
                return jsonify({"error": "Unauthorized"}), 401
        return wrapper

    def admin_or_user_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            username = request.authorization.username
            current_user = User.query.filter_by(username=username).first()
            if current_user:
                kwargs['current_user'] = current_user
                if current_user.role == "admin" or current_user.role == "user":
                    return fn(*args, **kwargs)
            return jsonify({"error": "Unauthorized"}), 401
        return wrapper


@app.route('/register/', methods=['POST'])
def add_user():
    data = request.get_json()
    if 'username' not in data or 'password' not in data:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Username and password must be provided'
        }), 400
    existing_user = User.query.filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({
            'error': 'Bad Request',
            'message': 'Username already exists'
        }), 400
    new_user = User(username=data['username'], password=data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully'}), 201


@app.route('/update/user/', methods=['PUT'])
@User.admin_or_user_required
def update_user(current_user):
    data = request.get_json()
    user = User.query.filter_by(username=current_user.username).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.password = data['password']
    db.session.commit() 
    return jsonify({'message': 'User updated successfully'}), 200

if __name__ == '__main__':
    app.run(host="127.0.0.1", port = 5000, debug=True)