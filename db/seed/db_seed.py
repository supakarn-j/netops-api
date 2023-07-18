import sys

sys.path.append("/home/ubuntu/netops_api")

from models.service import Service
from database import SessionLocal
import json

db = SessionLocal()
SEED_DATA = json.load(open("db/seed/service_seed.json", "r"))
print(SEED_DATA)

db.bulk_insert_mappings(Service, SEED_DATA)
db.commit()
db.close()