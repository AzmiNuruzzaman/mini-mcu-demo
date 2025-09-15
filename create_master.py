# create_master.py
from db import queries

MASTER_USERNAME = "master"
MASTER_PASSWORD = "Master123!"  # change as needed

# Add Master user
queries.add_user(MASTER_USERNAME, MASTER_PASSWORD, "Master")
print(f"Master user '{MASTER_USERNAME}' created with password '{MASTER_PASSWORD}'")
