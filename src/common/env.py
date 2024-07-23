import os

def get_token():
    return os.getenv('TOKEN')

def get_db_location():
    return os.getenv("DB_LOCATION")