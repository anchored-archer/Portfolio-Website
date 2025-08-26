import os
import frontmatter 
import time
import mistune 
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Type Checking Imports 
from typing import Tuple
from psycopg2.extensions import connection as Con, cursor as Cur

dotenv_path = "/home/wanderer/Desktop/Portfolio-Website/docker/.env"
load_dotenv()
print(os.environ["POSTGRES_PASSWORD"])

def createdb_ifnotexists(database: str) -> Tuple[Con, Cur]:
    """
    Given a database name, connects to it. If it doesn't exist, connects to the master database and creates it. 
    """
    password: str = os.environ["POSTGRES_PASSWORD"] 
    try:
        con = psycopg2.connect(f"dbname={database} user=postgres password={password} host=db port=5432")
    except psycopg2.OperationalError:
        # Create database, and close the autocmiit connection
        con: object = psycopg2.connect(f"dbname=postgres user=postgres password={password} host=db port=5432")
        con.set_session(autocommit=True)
        cur: object = con.cursor()
        cur.execute(sql.SQL("CREATE database {}").format(sql.Identifier(database)))

        cur.close()
        con.close()

        # Connect to the new database
        con = psycopg2.connect(f"dbname={database} user=postgres password={password} host=db port=5432")

    cur: object = con.cursor()
    return con, cur

def check_modfied(cur, filepath) -> list | None:
    """
    Given A filepath, and a database handeling object, check's if any modfication of file in the said path, is registrered to the db.
    """
    # Retrive L.M.D's from database 
    cur.execute(sql.SQL("SELECT last_modified_date FROM records;"))
    last_modfified_dates_db : list = [row[0] for row in cur.fetchall()]

    # Retrive L.M.D's from os
    last_modfified_dates_os : list = []
    directories : list = os.listdir()
    for filename in directories:
        if filename != ".obsidian":  
            timestamp = os.path.getmtime(filename)
            last_modified_date: str = time.strftime('%B %d %Y %I:%M:%S %p', time.localtime(timestamp))
            last_modfified_dates_os.append(last_modified_date)
    changed_LMDs : list = []
    
    # Check if the os's LMD databases's LMD match
    for last_modfified_date_db, last_modfified_date_os in zip(last_modfified_dates_db, last_modfified_dates_os):
        if last_modfified_date_db != last_modfified_date_os:
            changed_LMDs.append(last_modfified_date_os)
    
    # pulls up, and returns a list of filenames, whose lmd's where modfified; If no mod, returns None
    if len(changed_LMDs) != 0:
        filenames : list = []
        for filename in directories: 
            if filename != ".obsidian":  
                timestamp = os.path.getmtime(filename)
                last_modified_date : str = time.strftime('%B %d %Y %I:%M:%S %p', time.localtime(timestamp))

                for changed_date in changed_LMDs:
                    if last_modified_date == changed_date:
                        filenames.append(filename.rstrip('.md'))
        return filenames 
    else:
        return None

def run():
    database = Database()
    filepath = database.create_db()
    
    while True:
        entries = check_modfied(database.cur, filepath)
        if entries:
            for filename in entries:
                data_value, title_value, last_modified_date_value = database.retrive_entry_data_os(f"{filename}.md")
                database.cur.execute("UPDATE records SET data = %s, last_modified_date = %s WHERE title = %s", (data_value, last_modified_date_value, title_value))
                database.con.commit()
        time.sleep(600)

def convert_mdh(text: str) -> str:
    """ Converts a markdown into HTML """
    markdown = mistune.create_markdown()
    html = markdown(text)
    return str(html) 

class Database():
    def __init__(self, filepath = "blog/") -> None:
        self.cur = None
        self.con = None
        self.filepath = filepath
    
    def create_db(self):
        self.con, self.cur = createdb_ifnotexists("portfolio-database")
        self.cur.execute(sql.SQL("CREATE TABLE IF NOT EXISTS records (title TEXT NOT NULL UNIQUE, data TEXT NOT NULL UNIQUE, last_modified_date TEXT NOT NULL);"))

        # Intiate Search for written blogs
        absolute_blog_folder_path = self.filepath
        os.chdir(absolute_blog_folder_path)
        files = os.listdir()

        # Create database useing files, their contents, metadata
        for file in files:
            # Retrive Info About filename
            if file != ".obsidian":
                data, title, last_modified_date = self.retrive_entry_data_os(file)
                self.title = title            
                
                # Fill Database
                try:
                    self.cur.execute("""INSERT INTO records (title, data, last_modified_date) VALUES (%s,%s,%s);""",(title,data,last_modified_date))
                except psycopg2.IntegrityError:
                    self.con.rollback()
                    self.cur.execute("UPDATE records SET data = %s, last_modified_date = %s WHERE title = %s", (data, last_modified_date, title))
                    continue
                self.con.commit()
            else:
                continue
        
        return absolute_blog_folder_path
    
    def retrive_entry_data_os(self : object, filename : str) -> tuple[str, str, str]:
        """Retrives data about a specific blog file from the os"""
        markdown_file_object: object = frontmatter.load(filename)
        text: str = markdown_file_object.content
        timestamp = os.path.getmtime(filename)

        data: str = convert_mdh(text)
        title: str = filename.rstrip('.md')
        last_modified_date: str = time.strftime('%B %d %Y %I:%M:%S %p', time.localtime(timestamp))

        return data, title, last_modified_date
    

# # # Create Database
# database = Database()
# cur, filepath, self = database.create_db()
