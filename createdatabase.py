from reviewanalysis import app, db

db.create_all()
print(db.__repr__)