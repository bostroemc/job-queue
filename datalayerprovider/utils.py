import os 
import sys
import signal
import time
import sqlite3
from sqlite3 import Error
import names
import random
import json

# initialize database connection, adding tables queue and history if required
def initialize(db):
    conn = None
    try:
        conn = sqlite3.connect(db, uri=True)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS queue (id integer PRIMARY KEY AUTOINCREMENT, job_order text, time_in text, time_out text);")
        c.execute("CREATE TABLE IF NOT EXISTS history (id integer PRIMARY KEY, job_order text, time_in text, time_out text);")

        return conn
 
    except Error as e:
        print(e)

    return conn   

# add job order to queue
def add_job_order(conn, job_order):
    try:
        time_in = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   
  
        c = conn.cursor()
        c.execute("INSERT INTO queue(job_order, time_in) VALUES(?, ?);", (job_order, time_in))
        conn.commit()

        return c.lastrowid
    
    except Error as e:
        print(e)  

def add_virtual_job_order(conn, qty):
    for x in range(qty):
        name = [names.get_first_name(), names.get_last_name()]
        email = f"{name[0]}.{name[1]}@email.com"
        job_order = {"name":[name[0], name[1]], "email":email, "company": "virtual", "color": [get_ball(), get_ball(), get_ball()]}
        add_job_order(conn, json.dumps(job_order))


# return queue count
def count_queue(conn):
    c = conn.cursor()
    history = c.execute("SELECT * FROM queue")
    return len(history.fetchall())

# return history count
def count_history(conn):
    c = conn.cursor()
    history = c.execute("SELECT * FROM history")
    return len(history.fetchall())

#fetch queue 
def fetch_queue(conn, limit, offset):
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM queue LIMIT ? OFFSET ?", [limit, offset])       
    result =  c.fetchall()

    if result:   
        r = [dict((c.description[i][0], value) for i, value in enumerate(row)) for row in result]
        return r

#fetch_history
def fetch_history(conn, limit, offset):
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC LIMIT ? OFFSET ?", [limit, offset])       
    result =  c.fetchall()

    if result:   
        r = [dict((c.description[i][0], value) for i, value in enumerate(row)) for row in result]
        return r        

#dump queue (history table unchanged)
def dump(conn):
    c = conn.cursor()
    c.execute("DELETE FROM queue")
    conn.commit()

#pop row from queue and transfer it to history table
def pop(conn):
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM queue LIMIT 1")
    result = c.fetchone()

    if result:
        r = [dict((c.description[i][0], value) for i, value in enumerate(result))]

        c.execute("INSERT INTO history SELECT * FROM queue LIMIT 1")
        c.execute('DELETE FROM queue LIMIT 1;',)
        conn.commit()

        return r  

#update item in history table with done status (i.e. update time_out)
def done(conn, id):
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    time_out = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())   

    c.execute("SELECT * FROM history WHERE id = ?", [id])
    result = c.fetchone()
    if result:
        r = [dict((c.description[i][0], value) for i, value in enumerate(result))]

        if r[0]['time_out'] is None:
            c.execute("UPDATE history SET time_out = ? WHERE id = ?", [time_out, id])
            conn.commit()   

            return r      

# create connection without inserting tables (not used)
def create_connection(db):
    conn = None
    try:
        conn = sqlite3.connect(db, uri=True)
        return conn
    
    except Error as e:
        print(e)

    return conn       

# generate random ball
def get_ball():
    color = ["red", "white", "blue"]
    return color[random.randint(0,2)]     