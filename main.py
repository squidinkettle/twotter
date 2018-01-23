import sqlite3
from urllib import urlopen
import json
from json import dumps
import requests
from flask import Flask, render_template,request, jsonify,g, redirect,url_for, session, logging, flash
import oauth2 as oauth
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from flask_ckeditor import CKEditorField, CKEditor
from functools import wraps
from sqlalchemy import create_engine
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

#Allows the posting and the editing of longer texts (its magic basically)
ckeditor = CKEditor(app)

#Sqlite3 init
def database():
    conn = sqlite3.connect('user_info.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    name VARCHAR(100), 
    email VARCHAR(100),
    username VARCHAR(30), 
    password VARCHAR(100), 
    register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);""")
    return c, conn

#table for twoots
def twoots_db():
    conn = sqlite3.connect('user_info.db')
    c = conn.cursor()
    query = '''CREATE TABLE IF NOT EXISTS twoots(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author VARCHAR (200),
        body TEXT,
        create_date DATE DEFAULT (datetime('now','localtime')))'''
    c.execute(query)
    return c, conn
    
#wrapper which checks if logged in   
def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
        if 'logged_in' in session:
            return f(*args,**kwargs)
        else:
            flash('Cant let you do that, chikibriki', 'danger')
            return redirect(url_for('login'))
    return wrap
    
#Main page, will include a login/register option and a small introduction to Twotter
@app.route('/')
def main_page():
    return render_template('main_page.html')

#class forms (2) one for registry and another for twooting
class RegisterForm(Form):
    name = StringField('Name',[validators.Length(min = 1, max =50)])
    email = StringField('Email', [validators.Length(min = 4, max = 50)])
    username = StringField('Username', [validators.Length(min = 6, max = 100)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message = 'Passwords do not match')
        
        ])
    confirm = PasswordField('Confirm password')
    
class PostForm(Form):
    body = StringField("What u thinkin'?", [validators.Length(min = 10, max = 100)])
    

#login page
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        c,conn = database()
        query = "SELECT password FROM users WHERE username = '%s'"%(username)
        c.execute(query)
        data = c.fetchone()
        if len(username) == 0:
            flash('Please fill in username thingy', 'danger')
            return redirect(url_for('login'))
        if data == None:
            flash('No username under that name', 'danger')
            return redirect(url_for('login'))
        
        password = data[0]
        if sha256_crypt.verify(password_candidate, password):
            flash("Login successful!", 'success')
            app.logger.info('PASSWORD GUT')
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('main_page'))
        else:
            app.logger.info('PASSWORD IS WRAUNG')
            error = 'Password not found'
            return render_template('login.html', error = error)
        conn.commit()
        conn.close()
    return render_template('login.html')
            

#register
@app.route('/register',methods = ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        c, conn = database()
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        query = "INSERT INTO users (name,email, username, password )VALUES('%s', '%s','%s','%s')"%(name,email,username,password)
        c.execute(query)
        conn.commit()
        conn.close()
        flash('Successfully registred!','success')
        return redirect(url_for('main_page'))
    return render_template('register.html', form = form)
 
 
    
#post twoot on feed
@app.route('/post_twoot', methods = ['GET', 'POST'])
@is_logged_in
def post_twoot():
    form = PostForm(request.form)
    if request.method == 'POST':
        body = form.body.data
        c, conn = twoots_db()
        query = "INSERT INTO twoots(author, body) VALUES ('%s','%s')"%(session['username'], body)
        c.execute(query)
        conn.commit()
        conn.close()
        flash('Post successful', 'success')
        return redirect('post_twoot')
    return render_template('post_twoot.html', form = form)

#logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main_page'))


#shows posted tweets
@app.route('/feed')
def feed():
    c, conn = twoots_db()
    query = '''SELECT * FROM twoots '''
    c.execute(query)
    feed = c.fetchall()
    conn.commit()
    conn.close()
    return render_template('feed.html',feed = feed)

@app.route('/remove_twoot/<string:id>')
@is_logged_in
def remove_twoot(id):
    c,conn = twoots_db()
    query = "DELETE FROM twoots WHERE id = '%s'"%(id)
    c.execute(query)
    conn.commit()
    conn.close()
    return redirect(url_for('feed'))

@app.route('/personal_posts')
@is_logged_in
def personal_posts():
    c,conn = twoots_db()
    query = "SELECT * FROM twoots WHERE author = '%s'"%(session['username'])
    c.execute(query)
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return render_template('personal_posts.html', rows = rows)
    
#test for twitter json information
@app.route('/legit_twitter')
def legit_twitter():
    #Enter twitter consumer and secret key
    Consumer_Key = ''
    Consumer_Secret = ''
    #Enter your access token and secret
    Access_Token = ''
    Access_Token_Secret	= ''
    
    consumer = oauth.Consumer(key = Consumer_Key, secret= Consumer_Secret)
    access_token = oauth.Token(key = Access_Token, secret = Access_Token_Secret)
    client = oauth.Client(consumer,access_token)
    
    timeline_endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=chabollin&count=99"
    
    response,data = client.request(timeline_endpoint)
    tweets = json.loads(data)
    info = 'text' #whatever you need to look for in twitter feed
    result = {'data':[{x:y}for y in tweets for x in y if info in x]} 
    
    return jsonify(result)
    #return (render_template('index.html',test = [x for x in tweets], test2 = tweets))
