from afcc.extensions import db, limiter
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

class User(db.Model):

    # The db table is called users, not User. Must specify this, otherwise SQLAlchemy assumes
    # that the table name is the same as the class name
    __tablename__ = 'users' 

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    deactivated = db.Column(db.Boolean, nullable=False, default=False)

    def set_password(self, password):
      self.password = generate_password_hash(password) # pbkdf2:sha256 is the encryption method used if none is specified.

    # # Remove the password so that views can freely pass this
    # def get_user_without_sensitive_data(self):
    #   user = query.filter_by(email=email).first()
    #   user.password = None
    #   return user

      