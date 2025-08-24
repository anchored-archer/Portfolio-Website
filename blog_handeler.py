import os
import frontmatter
import time
import mistune
import json
import sqlite3

def convert_mdh(text: str) -> str:
    """ Converts a markdown into HTML """
    markdown = mistune.create_markdown()
    html = markdown(text)
    return html

class Metadata():
    def __init__(self, title : str, metapath: str =  "C:/Users/ghosa/Desktop/Master Folder/Programing/portfolio-web/metadata") -> None:
        self.metapath = metapath
        self.title = title
    
    def pull_metadata(self) -> bool | Exception:
        """
        Pulls up the given metdata from the given filepath; returns error if unsucessful
        """
        self.metadata_path = f"{self.metapath}/{self.title}.json"
        try:
            with open(self.metadata_path, 'r') as metafile:
                metadata_str = metafile.read()
                metadata = json.loads(metadata_str)
            return metadata['accessed']
        
        except FileNotFoundError:
            raise FileNotFoundError
        
    def write_metadata(self, metadata: dict) -> bool | Exception:
        """
        Writes the given metadata to a ads_path --- 
        a path that constitues of the filepath to the object, 
        and the name of the variable in which metadata is stored in a string format. 
        "metadata" is the dictionary "contaning" the key, value pairs of the metadata that has to be written 
        """
        self.metadata_path = f"{self.metapath}/{self.title}.json"
        metadata_string = json.dumps(metadata)
        try:
            with open(self.metadata_path, 'w') as ads_file:
                ads_file.write(metadata_string)
            return metadata["accessed"]
        except:
            raise 

class Database(Metadata):
    def __init__(self, filepath = "C:/Users/ghosa/Desktop/Master Folder/Programing/portfolio-web/blog") -> None:
        super().__init__(title=None)
        self.con = None
        self.cur = None
        self.filepath = filepath

    
    def create_db(self):
        # Create SQLite Database
        self.con = sqlite3.connect("database.db")
        self.cur = self.con.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS records (title TEXT NOT NULL, data TEXT NOT NULL, last_modified_date TEXT NOT NULL, accessed BOOLEAN NOT NULL);")

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

            try: 
                accessed = self.pull_metadata()
            except FileNotFoundError:
                metadata = {"accessed": False}
                accessed = self.write_metadata(metadata)
            
            # Fill Database
            self.cur.execute("INSERT INTO records (title, data, last_modified_date, accessed) VALUES (?,?,?,?);", (title, data, last_modified_date, accessed))
            self.con.commit()

def check_changes():
    
    ...

def run():
    while True:
        time.sleep(600)
        check_changes()


# Create Database
database = Database()
database.create_db()