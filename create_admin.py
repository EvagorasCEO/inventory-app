from app import db, app, User

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin", password="1234")
        db.session.add(user)
        db.session.commit()
        print("✅ Δημιουργήθηκε ο χρήστης admin")
    else:
        print("ℹ️ Ο χρήστης admin υπάρχει ήδη")
