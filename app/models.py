from app import db
import sqlalchemy as sa

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

class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    venue = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(255), nullable=False)
    link = db.Column(db.String(255))
    start_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    org_name = db.Column(db.String(255), nullable=False)
    org_mail = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    banner = db.Column(db.Text)
    logo = db.Column(db.Text)
    privacy_type = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.User_id'), nullable=False)
    registration_start_date = db.Column(db.Date, nullable=False)
    registration_start_time = db.Column(db.Time, nullable=False)
    registration_end_date = db.Column(db.Date, nullable=False)
    registration_end_time = db.Column(db.Time, nullable=False)

    def __init__(self, name, venue, method, link, start_date, start_time, end_date, end_time, description, org_name, org_mail, type, banner, logo, privacy_type, user_id, registration_start_date, registration_start_time, registration_end_date, registration_end_time):
        self.name = name
        self.venue = venue
        self.method = method
        self.link = link
        self.start_date = start_date
        self.start_time = start_time
        self.end_date = end_date
        self.end_time = end_time
        self.description = description
        self.org_name = org_name
        self.org_mail = org_mail
        self.type = type
        self.banner = banner
        self.logo = logo
        self.privacy_type = privacy_type
        self.user_id = user_id
        self.registration_start_date = registration_start_date
        self.registration_start_time = registration_start_time
        self.registration_end_date = registration_end_date
        self.registration_end_time = registration_end_time