"""
This file contains decorators, which are functions that can be injected into views
to provide extra functionality.
"""

from functools import wraps
from flask import request, redirect, url_for
from flask_login import current_user

"""
Create a decorator to restrict what users can access if they haven't verified 
their email address
"""
def email_verification_required(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    if current_user.email_verified is False:
      return redirect(url_for('user.email_not_verified'))
    return f(*args, **kwargs)
  return decorated_function
