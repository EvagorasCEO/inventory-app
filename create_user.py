from app import db, User, app

with app.app_context():
    user = User(username="admin", password="1234")
    db.session.add(user)
    db.session.commit()
    print("✅ Ο χρήστης δημιουργήθηκε με επιτυχία!")
