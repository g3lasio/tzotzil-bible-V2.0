
from flask import Blueprint, jsonify, current_app, redirect, url_for, render_template
import stripe
from models import User, db
from flask_login import current_user, login_required
import logging

payment = Blueprint('payment', __name__)
logger = logging.getLogger(__name__)

stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')

@payment.route('/upgrade')
@login_required
def upgrade():
    try:
        return render_template('payment/upgrade.html')
    except Exception as e:
        logger.error(f"Error loading upgrade page: {str(e)}")
        return render_template('error.html', error="Error loading upgrade page"), 500

@payment.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': current_app.config.get('STRIPE_PRICE_ID'),
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('payment.success', _external=True),
            cancel_url=url_for('payment.cancel', _external=True),
            client_reference_id=str(current_user.id)
        )
        return jsonify({'sessionId': checkout_session.id})
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}")
        return jsonify({'error': str(e)}), 500

@payment.route('/success')
@login_required
def success():
    try:
        current_user.is_premium = True
        db.session.commit()
        return render_template('payment/success.html')
    except Exception as e:
        logger.error(f"Error updating user to premium: {str(e)}")
        return render_template('error.html', error="Error processing payment"), 500

@payment.route('/cancel')
def cancel():
    return render_template('payment/cancel.html')
