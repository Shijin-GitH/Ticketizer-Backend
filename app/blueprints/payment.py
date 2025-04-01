import razorpay
import os
from dotenv import load_dotenv
from flask import Flask, Blueprint, jsonify, request
import hmac
import hashlib
import logging

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
        
        # Create an order using Razorpay Orders API
        DATA = request.get_json()
        response = client.order.create(data=DATA)
        order_id = response.get("id")  # Extract the order_id from the response

        # Return the order_id to the frontend
        return jsonify({"order_id": order_id, "status": "success"}), 200
    except razorpay.errors.RazorpayError as e:
        # Handle errors and return a failure response
        return jsonify({"error": str(e), "status": "failure"}), 500
    
# Route to verify payment signature

@bp.route('/payment_callback', methods=['POST'])
def payment_callback():
    try:
        # Debug: Print the request data
        print("Request data:", request.data, flush=True)
        logging.debug(f"Request data: {request.data}")

        # Ensure the request Content-Type is application/json
        if not request.is_json:
            return jsonify({"error": "Unsupported Media Type: Content-Type must be application/json", "status": "failure"}), 415
        
        # Retrieve data from the callback
        data = request.get_json()
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")

        # Verify the signature
        secret = os.getenv("RZR_KEY_SECRET")
        generated_signature = hmac.new(
            bytes(secret, 'utf-8'),
            bytes(f"{razorpay_order_id}|{razorpay_payment_id}", 'utf-8'),
            hashlib.sha256
        ).hexdigest()

        if generated_signature == razorpay_signature:
            # Payment is authentic
            return jsonify({"status": "success", "message": "Payment verified successfully"}), 200
        else:
            # Signature mismatch
            return jsonify({"status": "failure", "message": "Invalid payment signature"}), 400
    except Exception as e:
        # Handle errors
        logging.error(f"Error: {str(e)}")
        return jsonify({"error": str(e), "status": "failure"}), 500


