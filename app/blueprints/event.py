from flask import Blueprint, request, jsonify
from app import db
from app.models import Event, User
from functools import wraps
import jwt
from flask import current_app

bp = Blueprint('event', __name__)

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

@bp.route('/create_event', methods=['POST'])
@token_required
def create_event(current_user):
    data = request.get_json()
    name = data.get('name')
    venue = data.get('venue')
    method = data.get('method')
    link = data.get('link')
    time_start = data.get('time_start')
    time_end = data.get('time_end')
    description = data.get('description')
    org_name = data.get('org_name')
    org_mail = data.get('org_mail')
    type = data.get('type')
    banner = data.get('banner')
    logo = data.get('logo')
    privacy_type = data.get('privacy_type')

    if not name or not method or not time_start or not time_end or not org_name or not org_mail or not type or not privacy_type:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Create a new event instance
        event = Event(
            name=name,
            venue=venue,
            method=method,
            link=link,
            time_start=time_start,
            time_end=time_end,
            description=description,
            org_name=org_name,
            org_mail=org_mail,
            type=type,
            banner=banner,
            logo=logo,
            privacy_type=privacy_type,
            user_id=current_user.User_id
        )

        # Add the event to the session and commit
        db.session.add(event)
        db.session.commit()

        return jsonify({'message': 'Event created successfully!', 'event_id': event.event_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/get_events', methods=['GET'])
def get_events():
    try:
        # Query all events
        events = Event.query.all()

        # Serialize the data
        data = []
        for event in events:
            data.append({
                'event_id': event.event_id,
                'name': event.name,
                'venue': event.venue,
                'method': event.method,
                'link': event.link,
                'time_start': event.time_start,
                'time_end': event.time_end,
                'description': event.description,
                'org_name': event.org_name,
                'org_mail': event.org_mail,
                'type': event.type,
                'banner': event.banner,
                'logo': event.logo,
                'privacy_type': event.privacy_type
            })

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/get_event/<int:event_id>', methods=['GET'])
def get_event(event_id):
    try:
        # Query the event by id
        event = Event.query.get(event_id)

        if event is None:
            return jsonify({'error': 'Event not found'}), 404

        # Serialize the data
        data = {
            'event_id': event.event_id,
            'name': event.name,
            'venue': event.venue,
            'method': event.method,
            'link': event.link,
            'time_start': event.time_start,
            'time_end': event.time_end,
            'description': event.description,
            'org_name': event.org_name,
            'org_mail': event.org_mail,
            'type': event.type,
            'banner': event.banner,
            'logo': event.logo,
            'privacy_type': event.privacy_type
        }

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/update_event/<int:event_id>', methods=['PUT'])
@token_required
def update_event(current_user, event_id):
    data = request.get_json()
    name = data.get('name')
    venue = data.get('venue')
    method = data.get('method')
    link = data.get('link')
    time_start = data.get('time_start')
    time_end = data.get('time_end')
    description = data.get('description')
    org_name = data.get('org_name')
    org_mail = data.get('org_mail')
    type = data.get('type')
    banner = data.get('banner')
    logo = data.get('logo')
    privacy_type = data.get('privacy_type')

    try:
        # Query the event by id
        event = Event.query.get(event_id)

        if event is None:
            return jsonify({'error': 'Event not found'}), 404
        if event.user_id == current_user.User_id or current_user.role == 'admin':
            # Update the event only with provided fields
            if name:
                event.name = name
            if venue:
                event.venue = venue
            if method:
                event.method = method
            if link:
                event.link = link
            if time_start:
                event.time_start = time_start
            if time_end:
                event.time_end = time_end
            if description:
                event.description = description
            if org_name:
                event.org_name = org_name
            if org_mail:
                event.org_mail = org_mail
            if type:
                event.type = type
            if banner:
                event.banner = banner
            if logo:
                event.logo = logo
            if privacy_type:
                event.privacy_type = privacy_type

            # Commit the changes
            db.session.commit()

            return jsonify({'message': 'Event updated successfully!'}), 200
        return jsonify({'error': 'Unauthorized access'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/delete_event/<int:event_id>', methods=['DELETE'])
@token_required
def delete_event(current_user, event_id):
    try:
        # Query the event by id
        event = Event.query.get(event_id)

        if event is None:
            return jsonify({'error': 'Event not found'}), 404
        if event.user_id == current_user.User_id or current_user.role == 'admin':
            # Delete the event
            db.session.delete(event)
            db.session.commit()
        else:
            return jsonify({'error': 'Unauthorized access'}), 403

        return jsonify({'message': 'Event deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500