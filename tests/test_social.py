from models.social_networks import GoogleAuth, LnAuth, FBAuth


def test_google():
    link = GoogleAuth().get_goo('https://localhost:7777/').url
    assert link.lower().startswith('https://') is True, 'Google Link Error'


def test_facebook():
    link = FBAuth().get_facebook('https://localhost:7777/').url
    assert link.lower().startswith('https://') is True, 'Facebook Link Error'


def test_linkedlin():
    link = LnAuth().get_ln('https://localhost:7777/').url
    assert link.lower().startswith('https://') is True, 'Linkedlin Link Error'


