import razorpay
import os
from dotenv import load_dotenv
from flask import Flask, Blueprint, jsonify, request, redirect
import hmac
import hashlib
import logging
from app.models import Transaction, Ticket, Event
from app import db
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize Razorpay client with your credentials
client = razorpay.Client(auth=(os.getenv('RZR_ID'), os.getenv("RZR_KEY")))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Define the blueprint
bp = Blueprint('payment', __name__)

@bp.route('/create_order', methods=['POST'])
def create_order():
    try:
        # Ensure the request Content-Type is application/json
        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json", "status": "failure"}), 415

        # Parse request data
        data = request.get_json()
        ticket_id = data.get('ticketId')
        event_token = data.get('eventToken')
        amount = data.get('amount')
        
        print(f"Received data: {data}")

        # Validate ticket and event
        ticket = Ticket.query.get(ticket_id)
        event = Event.query.filter_by(token=event_token).first()
        if not ticket or not event:
            return jsonify({"error": "Invalid ticket or event token", "status": "failure"}), 400

        # Create a new transaction
        transaction_id = str(uuid.uuid4())
        transaction = Transaction(
            transaction_id=transaction_id,
            ticket_id=ticket_id,
            event_id=event.event_id,
            amount=amount
        )
        db.session.add(transaction)
        db.session.commit()

        # Create an order using Razorpay Orders API
        razorpay_order = client.order.create(data={
            "amount": amount,
            "currency": "INR",
            "receipt": transaction_id
        })
        order_id = razorpay_order.get("id")
        
        # Store the order ID in the transaction
        transaction.order_id = order_id
        db.session.commit()

        # Return the order_id and transaction details to the frontend
        return jsonify({"order_id": order_id, "transaction_id": transaction_id, "status": razorpay_order.get("status")}), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "failure"}), 500

@bp.route('/payment_callback', methods=['POST'])
def payment_callback():
    try:
        frontend_url = os.getenv("FRONTEND_URL")
        # Retrieve data from the callback
        data = request.form.to_dict()
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")

        # Ensure required fields are present
        if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
            redirect_url = f"{frontend_url}/payment-failed"
            return redirect(redirect_url, code=302)

        # Get the transaction ID from the order ID
        transaction = Transaction.query.filter_by(order_id=razorpay_order_id).first()
        if not transaction:
            return jsonify({"error": "Invalid order ID", "status": "failure"}), 400
        transaction_id = transaction.transaction_id
    
        # Verify the signature
        secret = os.getenv("RZR_KEY")
        generated_signature = hmac.new(
            bytes(secret, 'utf-8'),
            bytes(f"{razorpay_order_id}|{razorpay_payment_id}", 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            redirect_url = f"{frontend_url}/{transaction_id}/payment-failed"
            return redirect(redirect_url, code=302)

        # Fetch the transaction
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            return jsonify({"error": "Invalid transaction ID", "status": "failure"}), 400

        # Update transaction status and Razorpay payment ID
        transaction.razorpay_payment_id = razorpay_payment_id
        transaction.status = "Success"
        db.session.commit()

        # Redirect to payment success page
        redirect_url = f"{frontend_url}/{transaction_id}/payment-success"
        return redirect(redirect_url, code=302)

    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e), "status": "failure"}), 500
    

# Route to get Event Name, Date and Ticket Name from Transaction ID

@bp.route('/transaction/<string:transaction_id>', methods=['GET'])
def get_transaction_details(transaction_id):
    try:
        transaction = Transaction.query.filter_by(transaction_id=transaction_id).first()
        if not transaction:
            return jsonify({"error": "Transaction not found", "status": "failure"}), 404

        ticket = Ticket.query.get(transaction.ticket_id)
        event = Event.query.get(transaction.event_id)

        if not ticket or not event:
            return jsonify({"error": "Ticket or Event not found", "status": "failure"}), 404

        response = {
            "event_name": event.name,
            "event_date": event.start_date.strftime("%Y-%m-%d"),
            "ticket_name": ticket.name,
            "amount": transaction.amount,
            "transaction_status": transaction.status
        }
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e), "status": "failure"}), 500
