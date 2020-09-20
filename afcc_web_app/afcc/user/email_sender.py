from afcc.extensions import mail
from flask import current_app
from flask_mail import Message

def send_confirmation_email(to, msg_template):
  email_msg = Message(
    'Please confirm your email address',
    recipients=[to],
    html=msg_template,
    sender=current_app.config['DEFAULT_MAIL_SENDER']
  )

  mail.send(email_msg)