import os
import frontmatter
import time
import mistune
import sqlite3

def check_modfied(cur, filepath) -> list | None:
    """
    Given A filepath, and a database handeling object, check's if any modfication of file in the said path, is registrered to the db.
    """
    # Retrive L.M.D's from database 
    cur.execute("SELECT last_modified_date FROM records;")
    last_modfified_dates_db : list = [row[0] for row in cur.fetchall()]

    # Retrive L.M.D's from os
    last_modfified_dates_os : list = []
    os.chdir(filepath)
    directories : list = os.listdir()
    for filename in directories:
        timestamp = os.path.getmtime(filename)
        last_modified_date: str = time.strftime('%B %d %Y', time.localtime(timestamp))
        last_modfified_dates_os.append(last_modified_date)
    changed_LMDs : list = []
    
    # Check if the os's LMD databases's LMD match
    for last_modfified_date_db, last_modfified_date_os in zip(last_modfified_dates_db, last_modfified_dates_os):
        if last_modfified_date_db != last_modfified_date_os:
            changed_LMDs.append(last_modfified_date_os)
    
    # pulls up, and returns a list of filenames, whose lmd's where modfified; If no mod, returns None
    if len(changed_LMDs) != 0:
        filenames : list = []
        for filename, changed_date in zip(directories, changed_LMDs): 
            timestamp = os.path.getmtime(filename)
            last_modified_date : str = time.strftime('%B %d %Y', time.localtime(timestamp))

            if last_modified_date == changed_date:
                filenames.append(filename.rstrip('.md'))
        
        return filenames 
    else:
        return None

def convert_mdh(text: str) -> str:
    """ Converts a markdown into HTML """
    markdown = mistune.create_markdown()
    html = markdown(text)
    return html

class Database():
    def __init__(self, filepath = "C:/Users/ghosa/Desktop/Master Folder/Programing/portfolio-web/blog") -> None:
        self.cur = None
        self.filepath = filepath
    
    def create_db(self):
        # Create SQLite Database
        self.con = sqlite3.connect("database.db")
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS records (title TEXT NOT NULL UNIQUE, data TEXT NOT NULL UNIQUE, last_modified_date TEXT NOT NULL);")

        # Intiate Search for written blogs
        absolute_blog_folder_path = self.filepath
        os.chdir(absolute_blog_folder_path)
        directories = os.listdir()

        # Create database useing files, their contents, metadata
        for filename in directories:
            filepath = f"{self.filepath}/{filename}"
            markdown_file_object = frontmatter.load(filepath)
            text = markdown_file_object.content
            timestamp = os.path.getmtime(filename)

            data = convert_mdh(text)
            title = filename.rstrip('.md')
            self.title = title
            last_modified_date = time.strftime('%B %d %Y', time.localtime(timestamp))
            
            # Fill Database
            try:
                self.cur.execute("INSERT INTO records (title, data, last_modified_date) VALUES (?,?,?);", (title, data, last_modified_date))
            except sqlite3.IntegrityError:
                continue
            self.con.commit()
        
        return self.cur, absolute_blog_folder_path

# Create Database
database = Database()
cur, filepath = database.create_db()

