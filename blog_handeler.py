import os
import frontmatter 
import time
import mistune 
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import subprocess

# Type Checking Imports 
from typing import Tuple
from psycopg2.extensions import connection as Con, cursor as Cur

load_dotenv()  # Docker injects env vars


def createdb_ifnotexists(database: str):
    password = os.environ["POSTGRES_PASSWORD"]
    while True:
        try:
            admin_con = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=password,
                host="db",
                port=5432,
            )
            admin_con.autocommit = True
            admin_cur = admin_con.cursor()
            break
        except psycopg2.OperationalError:
            print("Waiting for PostgreSQL...")
            time.sleep(2)
            
    admin_cur.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s", (database,)
    )
    exists = admin_cur.fetchone()

    if not exists:
        print(f"Creating database '{database}'")
        admin_cur.execute(
            sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database))
        )

    admin_cur.close()
    admin_con.close()

    while True:
        try:
            con = psycopg2.connect(
                dbname=database,
                user="postgres",
                password=password,
                host="db",
                port=5432,
            )
            cur = con.cursor()
            return con, cur
        except psycopg2.OperationalError:
            print(f"Waiting for database '{database}'...")
            time.sleep(2)

def get_git_commit_date(filepath: str) -> str | int:
    """
    Gets the last commit date for a file using Git.
    Returns the date as a formatted string.
    """
    try:
        # The command is broken into a list for security and correctness
        command = [
            "git", "log", "-1",
            "--pretty=format:%cd",
            "--date=format:%B %d %Y %I:%M:%S %p",
            "--",
            filepath
        ]
        
        # Execute the command
        result = subprocess.run(
            command,
            capture_output=True,  # Capture the command's output
            text=True,            # Decode the output as text
            check=True,           # Raise an exception if the command fails
            encoding='utf-8'      # Specify encoding
        )
        
        # The output is in result.stdout, strip any trailing newline
        return result.stdout.strip()
    except: 
        raise 


def check_modfied(cur, filepath) -> list[str] | None:
    # Fetch DB state
    cur.execute("SELECT title, last_modified_date FROM records;")

    # Get a dictionary up where title of blogs is key, and last_modified_date is the va
    db_state = {}
    for row in cur.fetchall():
        db_state[row[0]] = row[1]

    changed_files = []

    for filename in os.listdir(filepath):
        if filename == ".obsidian" or not filename.endswith(".md"):
            continue

        full_path = os.path.join(filepath, filename)
        title = filename[:-3]

        try:
            last_modified_date = get_git_commit_date(full_path)
        except:
            raise

        if title not in db_state or db_state[title] != last_modified_date:
            changed_files.append(full_path)

    return changed_files if changed_files else None


def run():
    database = Database()
    filepath = database.create_db()

    while True:
        entries = check_modfied(database.cur, filepath)

        if entries:
            for full_path in entries:
                data_value, title_value, last_modified_date_value = (
                    database.retrive_entry_data_os(full_path)
                )

                database.cur.execute(
                    "UPDATE records SET data = %s, last_modified_date = %s WHERE title = %s",
                    (data_value, last_modified_date_value, title_value),
                )
                database.con.commit()

        time.sleep(600)


def convert_mdh(text: str) -> str:
    """ Converts a markdown into HTML """
    class CustomRenderer(mistune.HTMLRenderer):
        def image(self, text, url, title=None):
            # This method ensures an image is always just an <img> tag
            return f'<img src="{url}" alt="{text}">'

    markdown = mistune.create_markdown(renderer=CustomRenderer())
    html = markdown(text)
    return str(html)

class Database():
    def __init__(self, filepath = "blog/") -> None:
        self.cur = None
        self.con = None
        self.filepath = filepath
    
    def create_db(self):
        self.con, self.cur = createdb_ifnotexists("portfolio-database")
        self.cur.execute(
            "CREATE TABLE IF NOT EXISTS records ("
            "title TEXT NOT NULL UNIQUE, "
            "data TEXT NOT NULL, "
            "last_modified_date TEXT NOT NULL)"
        )

        files = os.listdir(self.filepath)

        for filename in files:
            if filename == ".obsidian":
                continue

            full_path = os.path.join(self.filepath, filename)

            data, title, last_modified_date = self.retrive_entry_data_os(full_path)

            try:
                self.cur.execute(
                    "INSERT INTO records (title, data, last_modified_date) VALUES (%s, %s, %s)",
                    (title, data, last_modified_date),
                )
                self.con.commit()
            except psycopg2.IntegrityError:
                self.con.rollback()
                self.cur.execute(
                    "UPDATE records SET data = %s, last_modified_date = %s WHERE title = %s",
                    (data, last_modified_date, title),
                )
                self.con.commit()

        return self.filepath

    
    def retrive_entry_data_os(self, filepath: str):
        markdown_file_object = frontmatter.load(filepath)
        text = markdown_file_object.content

        title = os.path.splitext(os.path.basename(filepath))[0]
        last_modified_date = get_git_commit_date(filepath)

        data = convert_mdh(text)
        return data, title, last_modified_date


