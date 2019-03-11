from norm.config import PUBLIC_USER, session


def login(usr=None):
    from norm.models.user import User
    if usr is None:
        usr = PUBLIC_USER

    u = session.query(User).filter(User.username == usr['username'],
                                   User.email == usr['email']).first()
    if u is None:
        u = User(**usr)
        session.add(u)
        session.commit()
    return u


# Initialize the user
try:
    user = login()
except:
    user = None



