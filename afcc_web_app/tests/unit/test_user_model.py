from afcc.user.models import User

def test_user_model_can_be_created():
  new_user = User(username='testuser', email='test@tesing.com', password='password')
  assert new_user.username == 'testuser'
  assert new_user.email == 'test@tesing.com'
  assert new_user.password == 'password'