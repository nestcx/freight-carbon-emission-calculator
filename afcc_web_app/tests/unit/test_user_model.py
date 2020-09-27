from afcc.user.models import User

def test_user_model_can_be_created():
  new_user = User(username='testuser', email='test@testing.com', password='password')
  assert new_user.username == 'testuser'
  assert new_user.email == 'test@testing.com'
  assert new_user.password == 'password'

def test_password_hashing():
  new_user = User(password='password')
  new_user.set_password(new_user.password)
  assert new_user.password != ''
  assert new_user.password != 'password'


def test_checking_password_hash():
  new_user = User(password='password')
  new_user.set_password(new_user.password)
  assert new_user.check_password('password') == True


def test_get_id():
  new_user = User(uid=1)
  assert new_user.get_id() == 1