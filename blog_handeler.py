import os
import frontmatter 
import time
import mistune 
import psycopg2
from dotenv import load_dotenv

# Type Checking Imports 
from typing import Tuple
from psycopg2.extensions import connection as Con, cursor as Cur

load_dotenv()

def createdb_ifnotexists(database: str) -> Tuple[Con, Cur]:
    password: str = os.environ["POSTGRES_PASSWORD"]
    try:
        con = psycopg2.connect(f"dbname={database} user=postgres password={password}")
    except psycopg2.OperationalError:
        con: object = psycopg2.connect(f"dbname=postgres user=postgres password={password}")
        cur: object = con.cursor()
        cur.execute("CREATE DATABASE %s;", database)
    else:
        cur: object = con.cursor()

    return con, cur

def check_modfied(cur, filepath) -> list | None:
    """
    Given A filepath, and a database handeling object, check's if any modfication of fifle in the said path, is registrered to the db.
    """
    # Retrive L.M.D's from database 
    cur.execute("SELECT last_modified_date FROM records;")
    last_modfified_dates_db : list = [row[0] for row in cur.fetchall()]

    # Retrive L.M.D's from os
    last_modfified_dates_os : list = []
    os.chdir(filepath)
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
        #TODO: REWRITTEN
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

def run(self, cur, filepath):
    entrys = check_modfied(cur, filepath)
    if entrys != None:
        for filename in entrys:
            data, title, last_modified_date = self.retrive_entry_data_os(f"{filename}.md")
            self.cur.execute("UPDATE records SET data = ?, last_modified_date = ? WHERE title = ?;", (data, last_modified_date, title))
            self.con.commit()
            time.sleep(600)

def convert_mdh(text: str) -> str:
    """ Converts a markdown into HTML """
    markdown = mistune.create_markdown()
    html = markdown(text)
    return str(html) 

class Database():
    def __init__(self, filepath = "C:/Users/ghosa/Desktop/Master Folder/Programing/portfolio-web/blog") -> None:
        self.cur = None
        self.con = None
        self.filepath = filepath
    
    def create_db(self):
        self.con, self.cur = createdb_ifnotexists("portfolio-database.db")
        self.cur.execute("CREATE TABLE IF NOT EXISTS records (title TEXT NOT NULL UNIQUE, data TEXT NOT NULL UNIQUE, last_modified_date TEXT NOT NULL);")

        # Intiate Search for written blogs
        absolute_blog_folder_path = self.filepath
        os.chdir(absolute_blog_folder_path)
        directories = os.listdir()

        # Create database useing files, their contents, metadata
        for filename in directories:
            # Retrive Info About filename
            if filename != ".obsidian":
                data, title, last_modified_date = self.retrive_entry_data_os(filename)
                self.title = title            
                
                # Fill Database
                try:
                    self.cur.execute("INSERT INTO records (title, data, last_modified_date) VALUES (?,?,?);", (title, data, last_modified_date))
                except psycopg2.IntegrityError:
                    continue
                self.con.commit()
            else:
                continue
        
        return self.cur, absolute_blog_folder_path, self
    
    def retrive_entry_data_os(self : object, filename : str) -> tuple[str, str, str]:
        """Retrives data about a specific blog file from the os"""
        filepath: str = f"{self.filepath}/{filename}" #type: ignore
        markdown_file_object: object = frontmatter.load(filepath)
        text: str = markdown_file_object.content
        timestamp = os.path.getmtime(filename)

        data: str = convert_mdh(text)
        title: str = filename.rstrip('.md')
        last_modified_date: str = time.strftime('%B %d %Y %I:%M:%S %p', time.localtime(timestamp))

        return data, title, last_modified_date

# # Create Database
database = Database()
cur, filepath, self = database.create_db()
