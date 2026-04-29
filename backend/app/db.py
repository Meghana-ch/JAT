import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="jobtracker",
        user="meghana_chikkam",
        password=""
    )
    return conn