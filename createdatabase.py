from reviewanalysis import app, db
from reviewanalysis.models import APItable


# # Inside the Python shell or script where you need to perform database operations:
# db.create_all()
# print(db.__repr__)
key_record = APItable.query.filter_by(api_key="d62ffb9f60cd7104b885c5248e8bb17a").first()
try:
    print(f"{key_record.api_key}    {key_record.usage_count}")
except Exception as e:
    print(e)