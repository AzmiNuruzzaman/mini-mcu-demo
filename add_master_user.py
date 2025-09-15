# add_master_user.py
from db.queries import get_user_by_username, add_user

# Check if master already exists
if get_user_by_username("master") is None:
    add_user("master", "master123", "Master")
    print("✅ Master account created.")
else:
    print("⚠️ Master account already exists.")
