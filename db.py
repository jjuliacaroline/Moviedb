import sqlite3
from flask import g

def get_connection():
    con = sqlite3.connect("database.db")
    con.execute("PRAGMA foreign_keys = ON")
    con.row_factory = sqlite3.Row
    return con

def execute(sql, params=[]):
    with get_connection() as con:
        cur = con.execute(sql, params)
        con.commit()
        g.last_insert_id = cur.lastrowid
        return cur

def last_insert_id():
    return getattr(g, "last_insert_id", None)

def query(sql, params=[]):
    with get_connection() as con:
        cur = con.execute(sql, params)
        rows = cur.fetchall()
    return [dict(row) for row in rows]
