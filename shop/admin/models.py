from shop import db, create_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer

# Define User DataModel
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    profile = db.Column(db.String(200), nullable=False, default='profile.jpg')

    def get_token(self, expires_sec=300):
        app = create_app()
        serial = TimedJSONWebSignatureSerializer(app.config["SECRET_KEY"], expires_in=expires_sec )
        return serial.dumps({'user_id':self.id}).decode('utf-8')
    
    @staticmethod
    def verify_token(token):
        app = create_app()
        serial = TimedJSONWebSignatureSerializer(app.config["SECRET_KEY"])
        try:
            user_id = serial.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return '<User %r>' % self.username

