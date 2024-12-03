from reviewanalysis import app, db
from reviewanalysis.models import APItable


# # Inside the Python shell or script where you need to perform database operations:
# db.create_all()
# print(db.__repr__)
key_record = APItable.query.all("api_key").first()
print(key_record)
# try:
#     print(f"{key_record.api_key}    {key_record.usage_count}")
# except Exception as e:
#     print(e)