from flask import Blueprint, render_template, request, jsonify, abort, session,redirect
from .models import Employee
from .validation import *
import psycopg2
from psycopg2 import extras
from configparser import ConfigParser
import os

auth = Blueprint('auth', __name__)

# Configuration
config = ConfigParser()

# Read the config.ini file
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
config.read(config_path)

#database connection
conn = psycopg2.connect(
    host=config.get('conn', 'host'),
    port=config.get('conn', 'port'),
    database=config.get('conn', 'database'),
    user=config.get('conn', 'user'),
    password=config.get('conn', 'password')
)

@auth.route('/')
def login():
    return render_template('login.html')

@auth.route('/login/authenticate', methods=['GET','POST'])
def loginAuthentication():
    if request.method == 'POST':
        data = request.json
        if emp_login(data['emp_email'],data['emp_password']):
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM EMPLOYEE WHERE emp_email='"+data['emp_email']+"' AND emp_password = '"+data['emp_password']+"' AND emp_status = 'Active';")
            rows = cur.fetchone()
            cur.close()
            
            if rows:
                session['emp_id'] = rows['emp_id']
                session['emp_type'] = rows['emp_type']
                
                response_data = {"message": "Success"}
                return jsonify(response_data), 200
            else:
                abort(404)
            
    abort(404)
    
@auth.route('/logout', methods=['GET','POST'])
def logout():
    session.clear()
    return redirect('/?')

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method =='POST':
        data = request.json 
        if emp_register(data['emp_fname'],data['emp_mname'],data['emp_lname'],data['emp_email'],data['emp_password']):
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("SELECT * FROM EMPLOYEE WHERE emp_email='"+data['emp_email']+"' OR (emp_fname = '"+data['emp_fname']+"' AND emp_mname = '"+data['emp_lname']+"' AND emp_lname = '"+data['emp_fname']+"' );")
            rows = cur.fetchone()
            if rows:
                abort(404)
                
            cur = conn.cursor(cursor_factory=extras.RealDictCursor)
            cur.execute("INSERT INTO EMPLOYEE (emp_fname, emp_mname, emp_lname, emp_email, emp_password ) VALUES ( '"+data['emp_fname'].title()+"', '"+data['emp_mname'].title()+"','"+data['emp_lname'].title()+"','"+data['emp_email']+"', '"+data['emp_password']+"');")
            conn.commit()
            cur.close()  
            response_data = {"message": "Success"}
            return jsonify(response_data), 200
    abort(404)