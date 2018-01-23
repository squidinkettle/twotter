from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
import sqlite3

class User_id(Resource):
    def get(self):
        conn = sqlite3.connect('user_info.db')
        c = conn.cursor()
        query = c.execute("SELECT * FROM users;") # This line performs query and returns json result
        row = c.fetchall()
        return {'users': [i[0] for i in row]} # Fetches first column that is User ID
        
class Users(Resource):
    def get(self):
        conn = sqlite3.connect('user_info.db')
        c = conn.cursor()
        query = c.execute("SELECT name, email, username, register_date FROM users;")
        #row = c.fetchall()
        result = {'data':[{'name':row[0],
                    'email':row[1],
                    'username':row[2],
                    'register_date':row[3]
        }for row in c.fetchall()]}
        return jsonify(result)
class Twoots(Resource):
    def get(self, id):
        conn = sqlite3.connect('user_info.db')
        c = conn.cursor()        
        query = c.execute("SELECT * FROM users WHERE id=%d " %(id))
        result = {'data': [{'username':row[3]
        }for row in c.fetchall()]}
        return jsonify(result)
        
'''
import sqlite3

conn = sqlite3.connect('test.db')
c = conn.cursor()
query = c.execute("CREATE TABLE IF NOT EXISTS test_test (id INTEGER PRIMARY KEY AUTOINCREMENT, cosmonaut VARCHAR(100), snek VARCHAR(100));")
conn.commit()

row1 = c.execute("SELECT * FROM test_test")

row = c.fetchall()
print (row)
    



def test(x,y):
    conn = sqlite3.connect('test.db')
    c = conn.cursor()
    query = "INSERT INTO test_test(cosmonaut,snek) VALUES ('%s','%s')"%(x,y)
    c.execute(query)
    conn.commit()
    conn.close()
    
'''