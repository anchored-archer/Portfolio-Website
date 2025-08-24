import concurrent.futures
from psycopg2.extensions import connection as Con, cursor as Cur
import psycopg2
import os 
from psycopg2 import sql
from dotenv import load_dotenv  

dotenv_path = "/home/wanderer/Desktop/Portfolio-Website/docker/.env"
load_dotenv()

# portfolio-database.db
def retrive():
    database = "portfolio-database"
    password: str = os.environ["POSTGRES_PASSWORD"]
    con = psycopg2.connect(f"dbname={database} user=postgres password={password} host=db port=5432")
    cur = con.cursor()
    cur.execute("SELECT * FROM records;")
    Database_Retrival = cur.fetchall()
    return Database_Retrival

