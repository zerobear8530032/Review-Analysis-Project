from reviewanalysis import app, db
from reviewanalysis.models import APItable


db.create_all()
print(db.__repr__)
