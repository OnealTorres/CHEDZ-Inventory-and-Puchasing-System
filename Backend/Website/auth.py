from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return '<script>alert("LOGIN")</script>'

@auth.route('/logout')
def logout():
    return '<script>alert("LOGOUT")</script>'

@auth.route('/signin')
def signin():
    return '<script>alert("SIGNIN")</script>'