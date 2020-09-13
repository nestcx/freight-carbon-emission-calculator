from afcc.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

from flask_login import UserMixin, login_required

# This loads the user into the login_manager. It does this by retrieving a user from the
# db in which the user object's uid matches with id passed in as an argument.
@login_manager.user_loader
def load_user(id):
  return User.query.get(int(id))

# The UserMixin provides default implementations for methods that flask-login expects a user class to have
class User(UserMixin, db.Model):

    # The db table is called users, not User. Must specify this, otherwise SQLAlchemy assumes
    # that the table name is the same as the class name
    __tablename__ = 'users' 

    def set_password(self, password):
      # pbkdf2:sha256 is the encryption method used if none is specified.
      self.password = generate_password_hash(password)

    def check_password(self, password):
      return check_password_hash(self.password, password)

    # Override the default get_id method that UserMixin provides
    def get_id(self):
      return self.uid

    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    deactivated = db.Column(db.Boolean, nullable=False, default=False)
    email_verified = db.Column(db.Boolean, nullable=False, default=False)