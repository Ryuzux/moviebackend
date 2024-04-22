from flask import request, jsonify
from models import *

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
        'topup_id':new_topup.id,
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
            'topup_id':topup.id,
            'message': 'Top-up request confirmed successfully'
            }), 200
    else:
        return jsonify({
            'topup_id':topup.id,
            'error': 'Top-up request has already been confirmed'
            }), 400

