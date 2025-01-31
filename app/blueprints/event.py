from flask import Blueprint, request, jsonify
from app import db
from app.models import Event

bp = Blueprint('event', __name__)

@bp.route('/create_event', methods=['POST'])
def create_event():
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
            privacy_type=privacy_type
        )

        # Add the event to the session and commit
        db.session.add(event)
        db.session.commit()

        return jsonify({'message': 'Event created successfully!', 'event_id': event.event_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500