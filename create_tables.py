# # from database import Base, engine
# # from models import Employee, ActivityLog

# # print("🚀 Creating tables...")
# # Base.metadata.create_all(bind=engine)
# # print("✅ Tables created successfully!")

# from database import engine, Base
# from models import Employee, ActivityLog

# print("Creating database tables...")
# Base.metadata.create_all(bind=engine)
# print("✅ Tables created successfully!")

from database import db

# This ensures collections exist by inserting and deleting a dummy doc
collections = ["employees", "activity_logs"]

for col in collections:
    if col not in db.list_collection_names():
        db[col].insert_one({"init": True})
        db[col].delete_many({"init": True})
        print(f"✅ Created collection: {col}")
    else:
        print(f"ℹ️ Collection already exists: {col}")

print("🎉 MongoDB collections setup complete.")
