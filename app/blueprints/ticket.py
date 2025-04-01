from flask import Blueprint, jsonify, request
from app.models import Ticket, Event, User
from functools import wraps
import jwt
from flask import current_app
from app import db

bp = Blueprint('ticket', __name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(User_id=data['user_id']).first()
        except:
            return jsonify({'error': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Route to display all the tickets for a specific event

@bp.route('/<string:token>/tickets', methods=['GET'])
def display_tickets(token):
    try:
        event = Event.query.filter_by(token=token).first()
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        tickets = Ticket.query.filter_by(event_id=event.event_id).all()
        
        #Serialize data
        tickets_data = []
        for ticket in tickets:
            ticket_data = {
                'ticket_id': ticket.ticket_id,
                'event_id': ticket.event_id,
                'name': ticket.name,
                'price': ticket.price,
                'quantity': ticket.quantity,
                'sold': ticket.num_sold
            }
            tickets_data.append(ticket_data)
        return jsonify(tickets_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to create a new ticket for an event
@bp.route('/<string:token>/create_ticket', methods=['POST'])
@token_required
def create_ticket(current_user, token):
    data = request.get_json()
    ticket_name = data.get('name')
    ticket_price = data.get('price')
    ticket_quantity = data.get('quantity')
    
    if not ticket_name or not ticket_price or not ticket_quantity:
        return jsonify({'error': 'Ticket name, price, and quantity are required'}), 400
    try:
        # Query the event by ID
        event = Event.query.filter_by(token = token).first()
        
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        # Create a new ticket instance
        ticket = Ticket(event_id=event.event_id, name=ticket_name, price=ticket_price, quantity=ticket_quantity)
        
        # Add the ticket to the session and commit
        db.session.add(ticket)
        db.session.commit()
        
        return jsonify({'message': 'Ticket created successfully!', 'ticket_id': ticket.ticket_id}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to edit a ticket
@bp.route('/<int:ticket_id>/edit_ticket', methods=['PUT'])
@token_required
def edit_ticket(current_user, ticket_id):
    data = request.get_json()
    ticket_name = data.get('ticket_name')
    ticket_price = data.get('ticket_price')
    ticket_quantity = data.get('ticket_quantity')
    
    try:
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Update ticket details
        if ticket_name:
            ticket.ticket_name = ticket_name
        if ticket_price:
            ticket.ticket_price = ticket_price
        if ticket_quantity:
            ticket.ticket_quantity = ticket_quantity
        
        db.session.commit()
        return jsonify({'message': 'Ticket updated successfully!'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route to delete a ticket
@bp.route('/<int:ticket_id>/delete_ticket', methods=['DELETE'])
@token_required
def delete_ticket(current_user, ticket_id):
    try:
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
        
        if not ticket:
            return jsonify({'error': 'Ticket not found'}), 404
        
        # Delete the ticket
        db.session.delete(ticket)
        db.session.commit()
        return jsonify({'message': 'Ticket deleted successfully!'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

