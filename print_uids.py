# print_uids.py
import pandas as pd
from db.queries import get_engine

def list_checkup_uids():
    query = "SELECT uid FROM checkups ORDER BY tanggal DESC"
    df = pd.read_sql(query, get_engine())
    if df.empty:
        print("No checkup data found.")
    else:
        print("Available UIDs for testing:")
        for uid in df["uid"]:
            print(uid)

if __name__ == "__main__":
    list_checkup_uids()
