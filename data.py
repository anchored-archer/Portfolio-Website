from psycopg2.extensions import connection as Con, cursor as Cur
import psycopg2
import os 
from psycopg2 import sql
from dotenv import load_dotenv  
from bs4 import BeautifulSoup

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

    preview_text_list = []
    for entry in Database_Retrival:
        entry_data = entry[1]
        soup = BeautifulSoup(entry_data, "lxml")

        # Generate Preview Text
        entry_text = soup.p.text
        entry_text = entry_text.split("PREVIEW-CUTOFF")[0]

        preview_text_list.append([entry[0], entry_text, entry[2]])

    return preview_text_list

