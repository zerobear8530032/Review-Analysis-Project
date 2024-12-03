from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from reviewanalysis import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Registertable.query.get(int(user_id))

class Registertable(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    api_count = db.Column(db.Integer, default=0)
    

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Registertable.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}',{self.api_count})"


class APItable(db.Model, UserMixin):
    __tablename__ = 'api_table'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('registertable.id'), nullable=False)  # Foreign key to Registertable
    api_key = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Default to current time
    status = db.Column(db.String(20), default='active')
    usage_count = db.Column(db.Integer, default=0)
    
    # Relationship to Registertable
    user = db.relationship('Registertable', backref=db.backref('api_keys', lazy=True))

    def __repr__(self):
        return f'<API Key {self.api_key}>'


class ContactUstable(db.Model, UserMixin):
    __tablename__="contactus_table"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String,nullable=False)  
    email = db.Column(db.String(225), nullable=False)
    submit_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False) 
    message = db.Column(db.String(1200),nullable=False)
    
    def __repr__(self):
        return f"id('{self.id}', username'{self.username}',email '{self.email}',submit at{self.submit_at},message {self.message})"
