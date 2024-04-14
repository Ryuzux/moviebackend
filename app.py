from flask import request, jsonify
from models import *
from datetime import datetime, timedelta

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
    return jsonify({
        'message': 'Registered successfully'
        }), 201

@app.route('/update/user/', methods=['PUT'])
@User.admin_or_user_required
def update_user(current_user):
    data = request.get_json()
    user = User.query.filter_by(username=current_user.username).first()
    if not user:
        return jsonify({
            'error': 'User not found'
            }), 404
    if 'username' in data:
        user.username = data['username']
    if 'password' in data:
        user.password = data['password']
    db.session.commit() 
    return jsonify({
        'message': 'User updated successfully'
        }), 200

@app.route('/add/movie/', methods=['POST'])
@User.admin_required
def add_movie():
    data = request.get_json()
    existing_movie = Movie.query.filter_by(name=data['name']).first()
    if 'name' not in data:
        return jsonify({
            'error': 'name movie must be input'
        })
    if existing_movie:
        return jsonify({
            'error': "the movie currently airing"
        })
    if 'launching' not in data:
        return jsonify({
            'error': 'launhcing date must be input'
        })
    if 'ticket_price' not in data:
        return jsonify({
            'error': 'ticket price must be input'
        })
    mov = Movie(
        name = data['name'],
        launching = data['launching'],
        category_id = data['category_id'],
        ticket_price = data['ticket_price']
    )
    db.session.add(mov)
    db.session.commit()
    return jsonify({
        'id': mov.id,
        'name': mov.name,
        'launching': mov.launching.strftime('%Y-%m-%d'),
        'category_id': mov.category_id,
        'ticket_price': mov.ticket_price
    })

@app.route('/update/movie/', methods=['PUT'])
@User.admin_required
def update_movie():
    data = request.get_json()
    update_id = data.get('id')
    if not update_id:
        return jsonify({
            'error': 'id is required in the request'
            }), 400
    movie = Movie.query.get(update_id)
    if not movie:
        return jsonify({
            'error': 'Movie not found'
            }), 404
    if 'name' in data:
        movie.name = data['name']
    if 'launching' in data:
        movie.launching = data['launching']
    if 'category_id' in data:
        movie.category_id = data['category_id']
    if 'ticket_price' in data:
        movie.ticket_price = data['ticket_price']
    db.session.commit() 
    return jsonify({
        'message': 'Movie updated successfully'
        }), 200

@app.route('/add/schedule/', methods=['POST'])
@User.admin_required
def add_schedule():
    data = request.get_json()

    if 'movie_id' not in data or 'time' not in data:
        return jsonify({
            'error': 'movie_id and time must be provided'
            }), 400

    existing_schedule = Schedule.query.filter_by(movie_id=data['movie_id'], time=data['time']).first()
    if existing_schedule:
        return jsonify({
            'error': 'The schedule already exists'
            }), 400

    new_schedule = Schedule(
        movie_id=data['movie_id'],
        time=data['time'],
        theater_id=data['theater_id']
    )

    db.session.add(new_schedule)
    db.session.commit()

    return jsonify({
        'id': new_schedule.id,
        'movie_id': new_schedule.movie_id,
        'name': new_schedule.movie.name,
        'ticket_price': new_schedule.movie.ticket_price,
        'time': new_schedule.time.strftime('%H:%M'),
        'theater_id': new_schedule.theater_id,
        'remaining_days': f'{new_schedule.movie.active_movie()} days' 
    }), 201

@app.route('/update/schedule/', methods=['PUT'])
@User.admin_required
def update_schedule():
    data = request.get_json()
    update_id = data.get('id')
    if not update_id:
        return jsonify({
            'error': 'id is required in the request'
        })
    sch = Schedule.query.get(update_id)
    if not sch:
        return jsonify({
            'error': 'Schedule not found'
            }), 404
    if 'id' in data:
        sch.id = data['id']
    if 'time' in data:
        sch.time = data['time']
    if 'theater_id' in data:
        sch.theater_id = data['theater_id']

    db.session.commit()
    return jsonify({
        'id': sch.id,
        'movie_id': sch.movie_id,
        'theater_id': sch.theater_id,
        'name': sch.movie.name,
        'time': sch.time.strftime('%H:%M'),
        'remaining_days': f'{sch.movie.active_movie()} days' 
    }), 200

@app.route('/list/', methods=['GET'])
@User.admin_or_user_required
def list_movie(current_user):
    play_date_str = request.form.get('play_date')
    if not play_date_str:
        return jsonify({
            'error': 'play_date parameter is required'
            }), 400
    try:
        play_date = datetime.strptime(play_date_str, '%Y-%m-%d').date() 
    except ValueError:
        return jsonify({
            'error': 'Invalid date format'
            }), 400

    max_launching_date = play_date - timedelta(days=7)
    active_movies = Movie.query.filter(Movie.launching >= max_launching_date).all()

    movie_info = [{
        'id': movie.id,
        'name': movie.name,
        'category': movie.info_category.name,
        'ticket_price': f'Rp {movie.ticket_price}',
        'schedules': [{
            'time': schedule.time.strftime('%H:%M'),
            'theater': schedule.info_theater.room if schedule.info_theater else None
        } for schedule in movie.schedules]
    } for movie in active_movies]
    return jsonify(movie_info), 200

@app.route('/search/', methods=['GET'])
@User.admin_or_user_required
def search_movie(current_user):
    query = request.args.get('query')
    if not query:
        return jsonify({
            'error': 'Query parameter is required'
            }), 400
    
    name_results = Movie.query.filter(Movie.name.ilike(f"%{query}%")).all()
    category_results = Movie.query.join(Category).filter(Category.name.ilike(f"%{query}%")).all()
    search_results = name_results + category_results
    movie_info = [
        {
            'id': movie.id,
            'name': movie.name,
            'launching': movie.launching.strftime('%Y-%m-%d'),
            'category': movie.info_category.name,
            'remaining_days': f'{movie.active_movie()} days'
        }
        for movie in search_results
    ]
    return jsonify(movie_info), 200

@app.route('/topup/', methods=['POST'])
@User.admin_or_user_required
def topup(current_user):
    data = request.get_json()
    if 'amount' not in data:
        return jsonify({
            'error': 'amount must be provided'
            }), 400

    try:
        amount = int(data['amount'])
    except ValueError:
        return jsonify({
            'error': 'Amount must be an integer'
            }), 400

    user = User.query.filter_by(username=current_user.username).first()
    if not user:
        return jsonify({
            'error': 'User not found or does not match'
            }), 404

    new_topup = Topup(
        user_id=user.id,
        amount=amount,
        is_confirmed=False
    )
    db.session.add(new_topup)
    db.session.commit()

    return jsonify({
        'message': 'Top-up request submitted successfully'
        }), 200

@app.route('/confirm/topup/', methods=['PUT'])
@User.admin_required
def confirm_topup():
    topup_id = request.get_json('id')
    if not topup_id:
        return jsonify({
            'error': 'Top-up request ID not provided'
            }), 400

    topup = Topup.query.get(topup_id)
    if not topup:
        return jsonify({
            'error': 'Top-up request not found'
            }), 404

    if not topup.is_confirmed:
        topup.is_confirmed = True
        db.session.commit()

        user = User.query.get(topup.user_id)
        user.balance += topup.amount
        db.session.commit()

        return jsonify({
            'message': 'Top-up request confirmed successfully'
            }), 200
    else:
        return jsonify({
            'error': 'Top-up request has already been confirmed'
            }), 400

@app.route('/buy/ticket', methods=['POST'])
@User.admin_or_user_required
def buy(current_user):
    data = request.get_json()
    schedule_id = data.get('schedule_id')
    transaction_date = data.get('date')

    if not schedule_id or not transaction_date:
        return jsonify({
            'error': 'schedule_id and date must be input'
            }), 400

    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({
            'error': 'Schedule not found'
            }), 404

    transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()

    available_seat_count = schedule.info_theater.total_seat - Transaction.query.filter_by(schedule_id=schedule_id).filter_by(date=transaction_date).count()
    if available_seat_count <= 0:
        return jsonify({
            'error': 'No available seats for this schedule on the given date'
            }), 400

    ticket_price = schedule.movie.ticket_price
    if current_user.balance < ticket_price:
        return jsonify({
            'error': 'Insufficient balance'
            }), 400
    
    current_user.balance -= ticket_price
    new_transaction = Transaction(
        user_id=current_user.id,
        schedule_id=schedule_id,
        date=transaction_date
    )

    db.session.add(new_transaction)
    db.session.commit()

    return jsonify({
        'message': 'Ticket purchased successfully'
        }), 200


@app.route('/topmovie', methods=['GET'])
@User.admin_or_user_required
def most_popular_movie(current_user):
    movies = Movie.query.all()
    movie_ticket_counts = {}
    for movie in movies:
        ticket_count = Transaction.query.join(Schedule).filter(Schedule.movie_id == movie.id).count()
        movie_ticket_counts[movie.id] = ticket_count

    sorted_movies = sorted(movie_ticket_counts.items(),key=lambda x: x[1], reverse=True)

    top_5_movies = sorted_movies[:5]

    result = {
        'top_movies': [{
            'id': movie_id,
            'name': db.session.get(Movie,movie_id).name,
            'ticket_count': ticket_count
        } for movie_id, ticket_count in top_5_movies
        ]}
    return jsonify(result), 200



if __name__ == '__main__':
    app.run(host="127.0.0.1", port = 5000, debug=True)