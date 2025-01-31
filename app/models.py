from app import db

class User(db.Model):
    __tablename__ = 'users'
    User_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Name = db.Column(db.String(255), nullable=False)
    Email = db.Column(db.String(255), unique=True, nullable=False)
    Phone = db.Column(db.String(20))
    Address = db.Column(db.Text)
    Password_Hash = db.Column(db.String(255), nullable=False)
    Profile_Pic = db.Column(db.Text)

    def __init__(self, name, email, phone, address, password_hash, profile_pic):
        self.Name = name
        self.Email = email
        self.Phone = phone
        self.Address = address
        self.Password_Hash = password_hash
        self.Profile_Pic = profile_pic

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
    time_start = db.Column(db.DateTime, nullable=False)
    time_end = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text)
    org_name = db.Column(db.String(255), nullable=False)
    org_mail = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(255), nullable=False)
    banner = db.Column(db.Text)
    logo = db.Column(db.Text)
    privacy_type = db.Column(db.String(255), nullable=False)

    def __init__(self, name, venue, method, link, time_start, time_end, description, org_name, org_mail, type, banner, logo, privacy_type):
        self.name = name
        self.venue = venue
        self.method = method
        self.link = link
        self.time_start = time_start
        self.time_end = time_end
        self.description = description
        self.org_name = org_name
        self.org_mail = org_mail
        self.type = type
        self.banner = banner
        self.logo = logo
        self.privacy_type = privacy_type