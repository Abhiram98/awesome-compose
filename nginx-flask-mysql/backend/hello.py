import os
from flask import Flask
import mysql.connector


class DBManager:
    def __init__(self, database='example', host="db", user="root", password_file=None):
        pf = open(password_file, 'r')
        self.connection = mysql.connector.connect(
            user=user, 
            password=pf.read(),
            host=host, # name of the mysql service as set in the docker compose file
            database=database,
            auth_plugin='mysql_native_password'
        )
        pf.close()
        self.connection.autocommit = True
        self.cursor = self.connection.cursor(buffered=True)

    
    def populate_db(self):
        self.cursor.execute('DROP TABLE IF EXISTS blog')
        self.cursor.execute('CREATE TABLE blog (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255))')
        self.cursor.executemany('INSERT INTO blog (id, title) VALUES (%s, %s);', [(i, 'Blog post #%d'% i) for i in range (1,5)])
        self.connection.commit()
    
    def query_titles(self):
        self.cursor.execute('SELECT title, id FROM blog')
        rec = []
        for c in self.cursor.fetchall():
            # if c[1] == 1:
            #     try:
            #         count = int(c[0].split(':')[1]) + 1
            #     except:
            #         count = 1
            rec.append(c[0])
            try:
                count = int(c[0].split(':')[1]) + 1
            except:
                count = 1
            self.cursor.execute(f"UPDATE blog set title='Blog post #{c[1]}. Reads:{count}' WHERE id={c[1]}")

        
        return rec


server = Flask(__name__)
conn = None

@server.route('/')
def listBlog():
    global conn
    if not conn:
        conn = DBManager(password_file='/run/secrets/db-password')
        conn.populate_db()
    rec = conn.query_titles()

    response = ''
    for c in rec:
        response = response  + '<div>   Hello  ' + c + '</div>'
    return response


if __name__ == '__main__':
    server.run()
