import blog_handeler
import concurrent.futures
from psycopg2.extensions import connection as Con, cursor as Cur
import psycopg2
import os 
from psycopg2 import sql
from dotenv import load_dotenv

# portfolio-database.db
def retrive():
    database = "portfolio-database.db"
    password: str = os.environ["POSTGRES_PASSWORD"]
    con = psycopg2.connect(f"dbname={database} user=postgres password={password}")
    cur = con.cursor()
    Database_Retrival = cur.execute("SELECT * FROM records;")
    return Database_Retrival

def run_blog():
    "To be called when the server is being tun: concurrency jackshit"
    database = blog_handeler.Database()
    cur, filepath, self = database.create_db()
    with concurrent.futures.ThreadPoolExecutor() as executer:
        result = executer.submit(blog_handeler.run, self, cur, filepath)
    ...
