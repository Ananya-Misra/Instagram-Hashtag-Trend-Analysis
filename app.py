import time

from utils import validate_email
from flask.globals import request
from flask import session
from sqlalchemy import create_engine
from sqlalchemy import engine
from webdriver_manager.chrome import ChromeDriverManager
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from project_orm import User
from utils import *
import sqlite3
from bot2 import *

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
    print("fghjkljdddddddddddddd");
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
                    return redirect('/main')
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
        print("niceeeeeeeeeeeeeeeeee")
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password) >= 6:
                    if cpassword and cpassword == password:
                        db = opendb()
                        is_existing = db.query(User).filter(User.email == email).first()
                        if is_existing:
                            flash('Email already exists','danger')
                        else:
                            try:
                                newuser = User(name=name,email=email,password=password)
                                db = opendb()
                                db.add(newuser)
                                db.commit()
                                db.close()
                                flash('Registration successful','success')
                                return redirect('/')
                            except Exception as e:
                                flash('Some error occurred','danger')
                    else:
                        flash('Password does not match', 'danger')
                else:
                    flash('Password must be of 6 or more characters', 'danger')
            else:
                flash('Invalid Email', 'danger')
        else:
            flash('Invalid name, must be 3 or more characters', 'danger')
    return render_template('index.html',title='Register')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    return render_template('forgot.html',title='Forgot Password')

@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('home.html',title='Home')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        print('ellllllllllllllllllllllllllllllll')
        username = request.form.get("username")
        password = request.form.get("password")
        print(username)
        if username and password:
            session['insta_username'] = username
            session['insta_password'] = password
            mdriver = webdriver.Chrome(ChromeDriverManager().install())
            mdriver.get("https://www.instagram.com/")
            time.sleep(4)
            try:
                login(mdriver, session['insta_username'], session['insta_password'], 3)
                notnow = mdriver.find_element("xpath", "//button[contains(text(), 'Not Now')]")

                print(notnow)
                mdriver.quit()
                session['is_auth'] = True
                return redirect('/scrape')
            except Exception as e:
                print(e)
                print("Hellll nooooooooooooooooooooo")
            time.sleep(3)
            flash('Wrong credentials', 'danger')

    return render_template('main.html', title='Main')

@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    print("Its scrape timee 1-1")
    if 'is_auth' not in session or session['is_auth'] != True:
        flash('Wrong credentials', 'danger')

        return redirect('/main')
    if request.method == 'POST':
        scroll = int(request.form.get('scroll'))
        sleeptime = int(request.form.get('sleep'))
        time.sleep(sleeptime)
        print("Its scrape timeeeeeeeeeeeeeee", scroll)
        # if login successful
        try:
            mdriver = webdriver.Chrome(ChromeDriverManager().install())
            mdriver.get("https://www.instagram.com/")
            time.sleep(sleeptime)
            login(mdriver, session['insta_username'], session['insta_password'], sleeptime)
            skip_login_info(mdriver, sleeptime)
            turn_off_notif(mdriver, sleeptime)
            mdriver.get("https://www.instagram.com/explore")
            # set_window_size(mdriver)
            scroller(mdriver, 0,sleeptime)
            time.sleep(sleeptime + 1)
            fetched_posts = insta_posts(mdriver, scroll, sleeptime + 2)
            print(fetched_posts)
            print(f'len of posts {len(fetched_posts)}')
            fetched_data = getdata(mdriver, fetched_posts, sleeptime)
            print("The time for fetched data has come...................=^^=")
            print(fetched_data)
            dataframe = covert_data_to_df(fetched_data)
            convert_df_to_csv(dataframe)
            print(dataframe)
            tableName = save_dataframe(dataframe)
            mdriver = webdriver.Chrome(ChromeDriverManager().install())
            insertColPost("hashtag_" + tableName)
            readSqliteTable("hashtag_" + tableName, mdriver, sleeptime)
            print("hashtag_"+tableName)
        except Exception as e:
            print(e)
            print("The error")

    return render_template('scrapping.html', title='Scrapping')

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