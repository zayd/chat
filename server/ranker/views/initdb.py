from ranker import app, db, User

db.create_all()
admin = User('admin', 'admin', 'admin@example.com')
db.session.add(admin)
db.session.commit()
users = User.query.all()
print users