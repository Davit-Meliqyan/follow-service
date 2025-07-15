# app/db.py
from arango.client import ArangoClient
from arango.collection import StandardCollection, EdgeCollection

from .config import settings

print("[INFO] Connecting to ArangoDB...")

client = ArangoClient(hosts=settings.arango_url)

sys_db = client.db(
    "_system",
    username=settings.arango_user,
    password=settings.arango_password
)

if not sys_db.has_database(settings.arango_db):
    sys_db.create_database(settings.arango_db)
    print(f"[INFO] Database '{settings.arango_db}' created.")
else:
    print(f"[INFO] Database '{settings.arango_db}' already exists.")

db = client.db(
    settings.arango_db,
    username=settings.arango_user,
    password=settings.arango_password
)

if not db.has_collection("users"):
    db.create_collection("users")
    print("[INFO] Collection 'users' created.")
else:
    print("[INFO] Collection 'users' already exists.")

if not db.has_collection("follows"):
    db.create_collection("follows", edge=True)
    print("[INFO] Edge collection 'follows' created.")
else:
    print("[INFO] Edge collection 'follows' already exists.")

users: StandardCollection = db.collection("users")
follows: EdgeCollection = db.collection("follows")

print("[INFO] ArangoDB initialization completed successfully.")
