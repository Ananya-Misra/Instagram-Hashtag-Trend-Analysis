import json
import plotly.express as px
from flask import Flask, session, flash, redirect, render_template
from flask.globals import request
from sqlalchemy.orm import sessionmaker
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bot2 import *
from project_orm import User
from utils import *
import pandas as pd
# login page
app = Flask(__name__)
app.secret_key = "the basics of life with python"


def sql_fetch():
    con = sqlite3.connect(r'./hashtags.sqlite3')
    cursorObj = con.cursor()
    cursorObj.execute('SELECT name from sqlite_master where type= "table"')
    return [name[0] for name in cursorObj.fetchall() if '__' in name[0]]


def opendb():
    engine = create_engine('sqlite:///db.sqlite3')
    Session = sessionmaker(bind=engine)
    return Session()


# login page
@app.route('/', methods=['GET', 'POST'])
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
                    flash('Login successful', 'success')
                    return redirect('/main')
                else:
                    flash("Invalid Password", 'danger')
            else:
                flash('Wrong credentials', 'danger')
        else:
            flash('Invalid Email', 'danger')
    return render_template('index.html', title='Login')


@app.route('/signup', methods=['GET', 'POST'])
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
                        db = opendb()
                        is_existing = db.query(User).filter(User.email == email).first()
                        if is_existing:
                            flash('Email already exists', 'danger')
                        else:
                            try:
                                newuser = User(name=name, email=email, password=password)
                                db = opendb()
                                db.add(newuser)
                                db.commit()
                                db.close()
                                flash('Registration successful', 'success')
                                return redirect('/')
                            except Exception as e:
                                flash('Some error occurred', 'danger')
                    else:
                        flash('Password does not match', 'danger')
                else:
                    flash('Password must be of 6 or more characters', 'danger')
            else:
                flash('Invalid Email', 'danger')
        else:
            flash('Invalid name, must be 3 or more characters', 'danger')
    return render_template('index.html', title='Register')


@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgot.html', title='Forgot Password')


@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('home.html', title='Home')


@app.route('/check_credentials')
def check_credentials():
    mdriver = webdriver.Chrome(ChromeDriverManager().install())
    mdriver.get("https://www.instagram.com/")
    time.sleep(4)
    print(session.items())
    if (login(mdriver, session['insta_username'], session['insta_password'], 3)):
        session['is_auth'] = True
        flash('Successful', 'success')
        return redirect('/scrape')
    flash('Wrong Credentials', 'warning')
    time.sleep(3)
    return redirect('/main')


@app.route('/main', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            session['insta_username'] = username
            session['insta_password'] = password
            return redirect('/check_credentials')
        else:
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
        # if login successful
        try:
            mdriver = webdriver.Chrome(ChromeDriverManager().install())
            mdriver.get("https://www.instagram.com/")
            time.sleep(sleeptime)
            login(mdriver, session['insta_username'], session['insta_password'], sleeptime)
            skip_login_info(mdriver, sleeptime)
            # turn_off_notif(mdriver, sleeptime)
            mdriver.get("https://www.instagram.csom/explore")
            # set_window_size(mdriver)
            scroller(mdriver, 0, sleeptime)
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
            print("hashtag_" + tableName)
            return redirect('/chart')
        except Exception as e:
            print(e)
            print("The error")

    return render_template('scrapping.html', title='Scrapping')


@app.route('/about')
def about():
    return render_template('about.html', title='About Us')


@app.route('/logout')
def logout():
    if session.get('is_auth', False):
        session.clear()
    return redirect('/')


@app.route('/visualize')
def line_chart():
    """
  Doing a bunch of python
  Using a small example data set.
  """

    data = json.dumps([1.0, 2.0, 3.0])
    labels = json.dumps(["12-31-18", "01-01-19", "01-02-19"])
    return render_template("visualization.html", data=data,
                           labels=labels, max=17000)


@app.route('/chart', methods=['GET', 'POST'])
def chart():
    if request.method == 'POST':
        tag_size = request.form.get('tag_sifze')
    else:
        tag_size = 50
    all_insta_tables = []
    print(sql_fetch())
    for name in sql_fetch():
        all_insta_tables.append(sqlToDf(name))
        print(name+" --------------------------------------")
    print(all_insta_tables)
    df = pd.concat(all_insta_tables)
    df.sort_values(by='posts', ascending=False, inplace=True)
    fig = px.bar(df[:int(tag_size)], x='tag', y='posts', log_y=True, )
    idf = pd.concat(all_insta_tables)
    date_df = idf.groupby('date')['posts'].sum()
    fig1 = px.ecdf(date_df, date_df.index, 'posts')
    fig2 = px.bar(df[:50], x='tag', y='date', log_y=True, )
    out = df.drop(columns=['link', 'page', 'img']).copy()

    out.sort_values(by='date', ascending=True, inplace=True)
    tagdf = idf.groupby('tag')['posts'].sum().reset_index()
    tagdf.sort_values(by='posts', ascending=False, inplace=True)
    fig3 = px.pie(tagdf[:10], 'tag', 'posts')
    weekdf = idf.groupby(idf.date.dt.weekday)['tag'].count().reset_index()
    fig4= px.line(weekdf, 'date', 'tag')

    return render_template('charts.html', out=out.to_html(index=False), figure=fig.to_html(), figure1=fig1.to_html(),
                           figure2=fig2.to_html(),ts = tag_size,  figure3=fig3.to_html(),  figure4=fig4.to_html(),)


if __name__ == "__main__":
    app.run(debug=True)
