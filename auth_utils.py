from database.init_db import db, User
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(email, password, name=None):
    if User.query.filter_by(email=email).first():
        return None, "Email already registered"
    u = User(email=email, password_hash=generate_password_hash(password), name=name or email.split("@")[0])
    db.session.add(u)
    db.session.commit()
    return u, None

def verify_user(email, password):
    u = User.query.filter_by(email=email).first()
    if not u:
        return None
    if check_password_hash(u.password_hash, password):
        return u
    return None
