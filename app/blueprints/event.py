from flask import Blueprint, request, jsonify
from app import db
from app.models import Event, User, EventAdmin
from functools import wraps
import jwt
from flask import current_app
from datetime import datetime

bp = Blueprint('event', __name__)

# Decorator to check if the token is provided
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

# Create a new event
@bp.route('/create_event', methods=['POST'])
@token_required
def create_event(current_user):
    data = request.get_json()
    name = data.get('name')
    venue = data.get('venue')
    method = data.get('method')
    link = data.get('link')
    start_date = data.get('start_date')
    start_time = data.get('start_time')
    end_date = data.get('end_date')
    end_time = data.get('end_time')
    description = data.get('description')
    org_name = data.get('org_name')
    org_mail = data.get('org_mail')
    type = data.get('type')
    banner = data.get('banner')
    logo = data.get('logo')
    privacy_type = data.get('privacy_type')

    try:
        registration_start_date = datetime.strptime(data.get('registrationStartDate'), '%Y-%m-%d').date()
        registration_start_time = datetime.strptime(data.get('registrationStartTime'), '%H:%M:%S').time()
        registration_end_date = datetime.strptime(data.get('registrationEndDate'), '%Y-%m-%d').date()
        registration_end_time = datetime.strptime(data.get('registrationEndTime'), '%H:%M:%S').time()
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_time = datetime.strptime(end_time, '%H:%M:%S').time()
        
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date or time format'}), 400

    if not name or not method or not start_date or not start_time or not end_date or not end_time or not org_name or not org_mail or not type or not privacy_type or not registration_start_date or not registration_start_time or not registration_end_date or not registration_end_time:
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Create a new event instance
        event = Event(
            name=name,
            venue=venue,
            method=method,
            link=link,
            start_date=start_date,
            start_time=start_time,
            end_date=end_date,
            end_time=end_time,
            description=description,
            org_name=org_name,
            org_mail=org_mail,
            type=type,
            banner=banner,
            logo=logo,
            privacy_type=privacy_type,
            user_id=current_user.User_id,
            registration_start_date=registration_start_date,
            registration_start_time=registration_start_time,
            registration_end_date=registration_end_date,
            registration_end_time=registration_end_time
        )

        #Add event and event admin to the session and commit
        db.session.add(event)
        db.session.commit()
        
        return jsonify({'message': 'Event created successfully!', 'event_id': event.event_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get all events
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
                'start_date': event.start_date.strftime('%Y-%m-%d'),
                'start_time': event.start_time.strftime('%H:%M:%S'),
                'end_date': event.end_date.strftime('%Y-%m-%d'),
                'end_time': event.end_time.strftime('%H:%M:%S'),
                'description': event.description,
                'org_name': event.org_name,
                'org_mail': event.org_mail,
                'type': event.type,
                'banner': event.banner,
                'logo': event.logo,
                'privacy_type': event.privacy_type,
                'registration_start_date': event.registration_start_date.strftime('%Y-%m-%d'),
                'registration_start_time': event.registration_start_time.strftime('%H:%M:%S'),
                'registration_end_date': event.registration_end_date.strftime('%Y-%m-%d'),
                'registration_end_time': event.registration_end_time.strftime('%H:%M:%S')
            })

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get an event by id
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
            'start_date': event.start_date.strftime('%Y-%m-%d'),
            'start_time': event.start_time.strftime('%H:%M:%S'),
            'end_date': event.end_date.strftime('%Y-%m-%d'),
            'end_time': event.end_time.strftime('%H:%M:%S'),
            'description': event.description,
            'org_name': event.org_name,
            'org_mail': event.org_mail,
            'type': event.type,
            'banner': event.banner,
            'logo': event.logo,
            'privacy_type': event.privacy_type,
            'registration_start_date': event.registration_start_date.strftime('%Y-%m-%d'),
            'registration_start_time': event.registration_start_time.strftime('%H:%M:%S'),
            'registration_end_date': event.registration_end_date.strftime('%Y-%m-%d'),
            'registration_end_time': event.registration_end_time.strftime('%H:%M:%S')
        }

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Update an event by id
@bp.route('/update_event/<int:event_id>', methods=['PUT'])
@token_required
def update_event(current_user, event_id):
    data = request.get_json()
    name = data.get('name')
    venue = data.get('venue')
    method = data.get('method')
    link = data.get('link')
    start_date = data.get('start_date')
    start_time = data.get('start_time')
    end_date = data.get('end_date')
    end_time = data.get('end_time')
    description = data.get('description')
    org_name = data.get('org_name')
    org_mail = data.get('org_mail')
    type = data.get('type')
    banner = data.get('banner')
    logo = data.get('logo')
    privacy_type = data.get('privacy_type')
    registration_start_date = data.get('registrationStartDate')
    registration_start_time = data.get('registrationStartTime')
    registration_end_date = data.get('registrationEndDate')
    registration_end_time = data.get('registrationEndTime')

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_time = datetime.strptime(end_time, '%H:%M:%S').time()
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid date or time format'}), 400

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
            if start_date:
                event.start_date = start_date
            if start_time:
                event.start_time = start_time
            if end_date:
                event.end_date = end_date
            if end_time:
                event.end_time = end_time
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
            if registration_start_date:
                event.registration_start_date = registration_start_date
            if registration_start_time:
                event.registration_start_time = registration_start_time
            if registration_end_date:
                event.registration_end_date = registration_end_date
            if registration_end_time:
                event.registration_end_time = registration_end_time

            # Commit the changes
            db.session.commit()

            return jsonify({'message': 'Event updated successfully!'}), 200
        return jsonify({'error': 'Unauthorized access'}), 403
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
# Delete an event by id   
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
    
# Fetch all banners    
@bp.route('/fetch_banners', methods=['GET'])
def fetch_banners():
    try:
        # Query all events
        events = Event.query.all()

        # Serialize the data
        data = []
        for event in events:
            data.append({
                'banner': event.banner,
                'registration_start_date': event.registration_start_date.strftime('%Y-%m-%d'),
                'registration_end_date': event.registration_end_date.strftime('%Y-%m-%d'),
                'registration_start_time': event.registration_start_time.strftime('%H:%M:%S'),
                'registration_end_time': event.registration_end_time.strftime('%H:%M:%S')
            })

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Add an event admin   
@bp.route('/add_event_admin', methods=['POST'])
@token_required
def add_event_admin(current_user):
    data = request.get_json()
    email = data.get('email')
    event_id = data.get('event_id')
    
    try:
        # Query the user by email
        user = User.query.filter_by(Email=email).first()
        
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        
        # Query the event by id
        event = Event.query.get(event_id)
        
        if event is None:
            return jsonify({'error': 'Event not found'}), 404
        
        # Check if the current user is an event admin
        current_user_admin = EventAdmin.query.filter_by(event_id=event_id, user_id=current_user.User_id).first()
        
        if current_user_admin is None:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        #Create a new event_admin instance
        event_admin = EventAdmin(
            event_id=event_id,
            user_id=user.User_id
        )
        
        db.session.add(event_admin)
        db.session.commit()
        
        return jsonify({'message': 'Event admin added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
            
# Remove an event admin
@bp.route('/remove_event_admin', methods=['DELETE'])
@token_required
def remove_event_admin(current_user):
    data = request.get_json()
    email = data.get('email')
    event_id = data.get('event_id')
    
    try:
        # Query the user by email
        user = User.query.filter_by(Email=email).first()
        
        if user is None:
            return jsonify({'error': 'User not found'}), 404
        
        # Query the event by id
        event = Event.query.get(event_id)
        
        if event is None:
            return jsonify({'error': 'Event not found'}), 404
            
        # Check if the current user is an event admin
        event_admin_currentuser = EventAdmin.query.filter_by(event_id=event_id, user_id=current_user.User_id).first()
        
        if event_admin_currentuser is None:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Remove user as event admin
        event_admin = EventAdmin.query.filter_by(event_id=event_id, user_id=user.User_id).first()
        
        if event_admin is None:
            return jsonify({'error': 'User is not an event admin'}), 404
        
        db.session.delete(event_admin)
        db.session.commit()
        
        return jsonify({'message': 'Event admin removed successfully!'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Get all event admins
@bp.route('/get_event_admins/', methods=['GET'])
@token_required
def get_event_admins(current_user):
    data = request.get_json()
    event_id = data.get('event_id')
    try:
        # Query the event by id
        event = Event.query.get(event_id)
        
        if event is None:
            return jsonify({'error': 'Event not found'}), 404
        
        #Check if currentuser is an event admin
        event_admin_currentuser = EventAdmin.query.filter_by(event_id=event_id, user_id=current_user.User_id).first()
        
        if event_admin_currentuser is None:
            return jsonify({'error': 'Unauthorized access'}), 403
        
        # Query all event admins
        event_admins = EventAdmin.query.filter_by(event_id=event_id).all()
        admin_count = EventAdmin.query.filter_by(event_id=event_id).count()
        
        # Serialize the data
        data = []
        for event_admin in event_admins:
            user = User.query.get(event_admin.user_id)
            data.append({
                'name': user.Name,
                'email': user.Email,
            })
            
        return jsonify({'admins': data, 'admin_count': admin_count}), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500