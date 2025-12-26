from psycopg2.extensions import connection as Con, cursor as Cur
import psycopg2
import os 
from psycopg2 import sql
from dotenv import load_dotenv  
from bs4 import BeautifulSoup
from datetime import datetime
import re


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
        entry_text = ''
        # Find the first paragraph that contains text
        for p in soup.find_all('p'):
            if p.get_text(strip=True):
                entry_text = p.get_text()
                break
        
        entry_text = entry_text.split("PREVIEW-CUTOFF")[0]

        # Format Date
        datetime_object = datetime.strptime(entry[2], '%B %d %Y %I:%M:%S %p')
        formatted_date = datetime_object.strftime('%d %b %Y')

        # Add hyperlink to title
        link_title = entry[0].replace(" ", "-")
        entry_link = f'/blog/{link_title}'

        # Format Image 
        match = re.search(r'<img src="([^"]+)" alt="([^"]+)"', entry_data)

        if match:
            image_src = match.group(1)  
            alt_text = match.group(2)   
            preview_text_list.append([entry[0], entry_text, alt_text, image_src, formatted_date, entry_link])
    
    preview_text_list.reverse()
    return preview_text_list

def retrieve_single_blog(title: str):
    database = "portfolio-database"
    password: str = os.environ["POSTGRES_PASSWORD"]
    con = psycopg2.connect(f"dbname={database} user=postgres password={password} host=db port=5432")
    cur = con.cursor()
    cur.execute("SELECT * FROM records WHERE title=%s", (title,))
    blog_entry : tuple | None = cur.fetchone() 

    if blog_entry is None: # Random thing to stop vs code from complaining about possible None type
        return None
    
    blog_post = []
    blog_text = blog_entry[1] 
    blog_entry_text = blog_text.replace("PREVIEW-CUTOFF", "")
    soup = BeautifulSoup(blog_entry_text, "lxml")

    # Format Date
    datetime_object = datetime.strptime(blog_entry[2], '%B %d %Y %I:%M:%S %p')
    formatted_date = datetime_object.strftime('%d %b %Y')

    blog_post = [blog_entry[0], blog_entry_text, formatted_date]

    return blog_post

