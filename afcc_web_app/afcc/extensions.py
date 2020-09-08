"""
As we're using the application factory pattern for application creation, we have to
create the extension objects outside of the application. Basically, the extension objects
should not be created in the initial create_app() function of the main __init.py__ file.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager

db = SQLAlchemy()
limiter = Limiter(key_func=get_remote_address)
login_manager = LoginManager() # The login manager used for handling users logging in and staying authenticated
