from app import app, db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    user = User(username='admin', password_hash=generate_password_hash('444Dol77'), role='admin')
    db.session.add(user)
    db.session.commit()
    print("Пользователь создан!")