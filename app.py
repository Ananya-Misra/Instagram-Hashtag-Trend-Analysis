from utils import validate_email
from flask.globals import request
from flask import session
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from project_orm import User
from utils import *

from flask import Flask,session,flash,redirect,render_template,url_for

# login page 
app = Flask(__name__)
app.secret_key = "the basics of life with python"

def opendb():
    engine = create_engine('sqlite:///db.sqlite3')
    Session = sessionmaker(bind=engine)
    return Session()

#login page
@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and validate_email(email):
            db = opendb()
            user = db.query(User).filter(User.email == email).first()
            db.close()
            if user:
                if user.password == password:
                    session['id'] = user.id
                    session['username'] = user.name
                    session['is_auth'] = True
                    flash('Login successful','success')
                    return redirect('/home')
                else:
                    flash("Invalid Password", 'danger')
            else:
                flash('Wrong credentials','danger')
        else:
            flash('Invalid Email', 'danger')
    return render_template('index.html',title='Login')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password) >= 6:
                    if cpassword and cpassword == password:
                        try:
                            newuser = User(name=name,email=email,password=password)
                            db = opendb()
                            db.add(newuser)
                            db.commit()
                            db.close()
                            print(newuser)
                            flash('Registration successful','success')
                            return redirect('/')
                        except:
                            flash('Email account already exists','danger')
                    else:
                        flash('Password does not match', 'danger')
                else:
                    flash('Password must be of 6 or more characters', 'danger')
            else:
                flash('Invalid Email', 'danger')
        else:
            flash('Invalid name, must be 3 or more characters', 'danger')
    return render_template('signup.html',title='Register')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    return render_template('forgot.html',title='Forgot Password')

@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('home.html',title='Home')

@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/logout')
def logout():
    if session.get('is_auth',False):
        session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)