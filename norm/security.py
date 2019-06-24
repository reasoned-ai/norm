import logging
import traceback

user = None


def login(usr=None):
    global user
    u = None
    try:
        from norm.models.user import User
        from norm.config import PUBLIC_USER, session
        if usr is None:
            usr = PUBLIC_USER

        u = session.query(User).filter(User.username == usr['username'],
                                       User.email == usr['email']).first()
        if u is None:
            u = User(**usr)
            session.add(u)
            session.commit()

        user = u
    except Exception as e:
        user = None
        logging.warning('Login failed')
        logging.warning(e)
        logging.warning(traceback.print_exc())
    return u



