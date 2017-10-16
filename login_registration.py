from flask import Flask, request, redirect, render_template, session, flash, url_for, abort
import re
from mysqlconnection import MySQLConnector
import md5
import os, binascii
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = 'abcde12345fghij'
mysql = MySQLConnector(app,'login_registration_DB')

@app.route('/')
def index():
    query = "SELECT * FROM login_table"
    other = mysql.query_db(query)
    return render_template('index.html',all_emails=other)

@app.route("/progressreg", methods=["POST"])
def progressreg():
    first_name = request.form['first_name']
    
    last_name = request.form['last_name']

    email = request.form['email']
   
    password = request.form['password']
 
    password_conf = request.form['password_conf']
    

    if len(request.form['first_name']) <1 or len(request.form['last_name']) <1 or len(request.form['email']) <1 or len(request.form['password']) <1 or len(request.form['password_conf']) <1:
        flash("Please correct your information and fill in every field.")
        return redirect("/")
        
    elif len(request.form['first_name']) < 2 or len(request.form['last_name']) < 2:
        flash("Names need to be longer than 2 letters.!")
        return redirect("/")
       
    elif len(request.form['password']) < 8: 
        flash("Password needs to be longer than 8 characters.")
        return redirect("/")
        
    elif request.form['password']!= request.form['password_conf']:
        flash("Password and Password Confirmation did not match")
        return redirect("/")
        
    elif (request.form['first_name']).isalpha() == False or (request.form['last_name']).isalpha() == False:
        flash("Non-alphabetic characters in your name is not allowed.")
        return redirect("/")
        
    else:
        query = "SELECT EXISTS (SELECT * FROM login_table WHERE email = '" + email + "')"
        show_query = mysql.query_db(query)
        for dict in show_query:
            for key in dict:
                if dict[key] == 1:
                    flash('Email had been registered.')
                    return redirect('/')
                    
                else:
                    salt = binascii.b2a_hex(os.urandom(15))
                    hashed_pw = md5.new(password + salt).hexdigest()
                    query = "INSERT INTO login_table(first_name, last_name, email, salt, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :salt, :password, NOW(), NOW())"
                    data = {'first_name': first_name, 'last_name': last_name, 'email': email, 'salt': salt, 'password': hashed_pw}
                    mysql.query_db(query, data)
                

    return redirect('/success')

@app.route("/login")
def login():
    return render_template('login.html')
    print login

@app.route("/progresslog", methods=["POST"])
def progresslog():

    email = request.form['email']
    password = request.form['password']
    query = "SELECT * FROM login_table WHERE email = :email LIMIT 1"
    data = {'email': email}
    output = mysql.query_db(query, data)
    print output
    if len(output) != 0:
        encrypted_password = md5.new(password + output[0]['salt']).hexdigest()
        if output[0]['password'] == encrypted_password:
            session['id'] = output[0]['id']
            print session ['id']
            return redirect ('/success')
        else:
            flash ('Password incorrect')
    else:
        flash('Email does not exist in DB')
    return redirect('/login')

@app.route("/success")
def success():
    return render_template('success.html')

app.run(debug=True)   