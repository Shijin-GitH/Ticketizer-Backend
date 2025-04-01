from app import db
import sqlalchemy as sa
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import text

class User(db.Model):
    __tablename__ = 'users'
    User_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Phone = db.Column(db.String(20))
    Password_Hash = db.Column(db.String(255), nullable=False)
    Profile_Pic = db.Column(db.Text)
    role = db.Column(sa.Enum('admin', 'user', name='role_types'), default='user')

    def __init__(self, name, email, phone, password_hash, profile_pic, role='user'):
        self.Name = name
        self.Email = email
        self.Phone = phone
        self.Password_Hash = password_hash
        self.Profile_Pic = profile_pic
        self.role = role
        

    @property
    def formatted_user_id(self):
        return f'TZR{self.User_id}'
    
class EventAdmin(db.Model):
    __tablename__ = 'event_admins'
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.User_id'), nullable=False)
    __table_args__ = (
        db.PrimaryKeyConstraint('event_id', 'user_id'),
    )

    def __init__(self, event_id, user_id):
        self.event_id = event_id
        self.user_id = user_id

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.User_id'), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    venue = db.Column(db.String(255))
    privacy_type = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(255), nullable=False)
    banner = db.Column(db.String(255))  # Store Cloudinary URL
    org_name = db.Column(db.String(255), nullable=False)
    org_mail = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    mode = db.Column(db.String(255), nullable=False)  # Added mode column
    min_team = db.Column(db.Integer)  # Added min_team column
    max_team = db.Column(db.Integer)  # Added max_team column
    registration_start_date = db.Column(db.Date)  # Added registration start date
    registration_start_time = db.Column(db.Time)  # Added registration start time
    registration_end_date = db.Column(db.Date)  # Added registration end date
    registration_end_time = db.Column(db.Time)  # Added registration end time
    status = db.Column(sa.Enum('Published', 'Unpublished', name='event_status'), default='Unpublished')
    token = db.Column(db.String(255), unique=True, nullable=False)

    def __init__(self, name, user_id, start_date, start_time, end_date, end_time, privacy_type, method, org_name, org_mail, type, mode, token, status="Unpublished", banner=None, min_team=None, description=None, max_team=None, registration_start_date=None, registration_start_time=None, registration_end_date=None, registration_end_time=None, venue=None):
        self.name = name
        self.user_id = user_id
        self.description = description
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.venue = venue
        self.privacy_type = privacy_type
        self.method = method
        self.banner = banner  # Store Cloudinary URL here
        self.org_name = org_name
        self.org_mail = org_mail
        self.type = type
        self.mode = mode
        self.min_team = min_team
        self.max_team = max_team
        self.registration_start_date = registration_start_date
        self.registration_start_time = registration_start_time
        self.registration_end_date = registration_end_date
        self.registration_end_time = registration_end_time
        self.status = status
        self.token = token
        
# Trigger to add owner as event admin when event is created
@event.listens_for(Event, 'after_insert')
def receive_after_insert(mapper, connection, target):
    stmt = text("INSERT INTO event_admins (event_id, user_id) VALUES (:event_id, :user_id)")
    connection.execute(stmt, {'event_id': target.event_id, 'user_id': target.user_id})

class Ticket(db.Model):
    __tablename__ = 'tickets'
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    num_sold = db.Column(db.Integer, default=0)  # Track number of tickets sold

    def __init__(self, event_id, name, price, quantity, num_sold=0):
        self.event_id = event_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.num_sold = num_sold


class Transaction(db.Model):
    __tablename__ = 'transactions'
    transaction_id = db.Column(db.String(255), primary_key=True)  # Use a string for unique transaction IDs
    order_id = db.Column(db.String(255), unique=True, nullable=True)  # Added order_id column
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.ticket_id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Added amount column
    status = db.Column(sa.Enum('Incomplete', 'Success', 'Failed', name='transaction_status'), default='Incomplete')  # Added status column
    razorpay_payment_id = db.Column(db.String(255), nullable=True)  # Added Razorpay payment ID column

    def __init__(self, transaction_id, ticket_id, event_id, amount, order_id=None, status="Incomplete", razorpay_payment_id=None):
        self.transaction_id = transaction_id
        self.order_id = order_id
        self.ticket_id = ticket_id
        self.event_id = event_id
        self.amount = amount
        self.status = status
        self.razorpay_payment_id = razorpay_payment_id


class Registration(db.Model):
    __tablename__ = 'registrations'
    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.ticket_id'), nullable=True)  # Nullable for non-ticketed events
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=False)

    def __init__(self, name, email, phone, ticket_id=None):
        self.name = name
        self.email = email
        self.phone = phone
        self.ticket_id = ticket_id
        
#Function to decrement ticket quantity after registration
@event.listens_for(Registration, 'after_insert')
def decrement_ticket_quantity(mapper, connection, target):
    if target.ticket_id:
        ticket = Ticket.query.get(target.ticket_id)
        if ticket and ticket.quantity - ticket.num_sold > 0:
            ticket.num_sold += 1
            db.session.commit()
        else:
            raise Exception("No tickets available for this event.")


class FormQuestion(db.Model):
    __tablename__ = 'form_questions'
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    question_type = db.Column(sa.Enum('text', 'select', 'radio', 'checkbox', name='question_types'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=True)  # Store options as a JSON string for select, radio, or checkbox types

    def __init__(self, event_id, question_type, question, options=None):
        self.event_id = event_id
        self.question_type = question_type
        self.question = question
        self.options = options


class FormAnswer(db.Model):
    __tablename__ = 'form_answers'
    answer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('form_questions.question_id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)  # Store answers as JSON for multiple answers (checkbox)

    def __init__(self, question_id, answer):
        self.question_id = question_id
        self.answer = answer


class TermsAndConditions(db.Model):
    __tablename__ = 'terms_and_conditions'
    term_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def __init__(self, event_id, content):
        self.event_id = event_id
        self.content = content