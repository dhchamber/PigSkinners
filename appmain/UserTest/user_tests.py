import pytest

from django.contrib.auth.models import User

@pytest.mark.django_db
def test_super_user():
    super_user = User.objects.get(id=1)
    assert super_user.username == 'footballpool'
    assert super_user.first_name == 'Random'
    assert super_user.last_name == 'Picks'
    assert super_user.is_superuser

