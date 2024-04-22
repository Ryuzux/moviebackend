from flask import request, jsonify
from models import *
from werkzeug.security import generate_password_hash

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
    
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=16)

    new_user = User(username=data['username'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'message': 'Registered successfully'
    }), 201

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
        user.password = generate_password_hash(data['password'], method='pbkdf2:sha256', salt_length=16)
    
    db.session.commit() 
    return jsonify({'message': 'User updated successfully'}), 200

@app.route('/user/')
@User.admin_or_user_required
def user(current_user):
    return jsonify({
      'username': current_user.username,
      'balance': current_user.balance,
      'id': current_user.id  
    })