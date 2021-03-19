from flask import Flask, render_template, request, redirect, request
import datetime
import sqlite3

app = Flask(__name__)

@app.before_first_request
def runsetup():
    conn = None
    try:
        conn = sqlite3.connect("db/sqldb.db")
        c = conn.cursor()
        tablecreatesql = '''
                            CREATE TABLE IF NOT EXISTS jars (
                                jar_id INTEGER PRIMARY KEY,
                                jar_name TEXT NOT NULL,
                                coin_value INTEGER DEFAULT 25
                            );
                            CREATE TABLE IF NOT EXISTS adds (
                                add_id INTEGER PRIMARY KEY,
                                name TEXT NOT NULL,
                                timestamp INTEGER NOT NULL,
                                jar INTEGER,
                                FOREIGN KEY(jar) REFERENCES jars(jar_id)
                            );
                        '''
        c.executescript(tablecreatesql)
        sqlquery = "SELECT * FROM jars;"
        c.execute(sqlquery)
        data = c.fetchone()
        if not data:
            insertrow = '''
                            INSERT INTO jars (jar_name, coin_value) VALUES ('MUTE JAR', 25)
                        '''
            c.execute(insertrow)
            conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

@app.route('/', methods=['GET','POST'])
def home():
    total = 0
    username = ""
    conn = sqlite3.connect("db/sqldb.db")
    c = conn.cursor()
    if request.method == "POST":
        username = "None"
        if request.form["username"]:
            username = request.form["username"]
        sqlinsert = "INSERT INTO adds (name, timestamp, jar) VALUES (:name, :timestamp, :jar)"
        c.execute(sqlinsert, {'name':username, 'timestamp':datetime.datetime.now(), 'jar':1})
        conn.commit()
    sqlquery = "SELECT * FROM jars;"
    c.execute(sqlquery)
    data = c.fetchone()
    title = data[1]
    pricepercoin = data[2] / 100
    sqlquery = "SELECT name, count(add_id) as coincount FROM adds WHERE jar=1 GROUP BY name"
    c.execute(sqlquery)
    data = c.fetchall()
    namelist = list()
    for entry in data:
        namelist.append({"name":entry[0], "owed":"$%.2f" % (entry[1] * pricepercoin)})
        total += entry[1] * pricepercoin
    totalvalue = "$%.2f" % total
    return render_template('coinjar.html', title=title, totalvalue=totalvalue, namelist=namelist, username=username)