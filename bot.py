# twilightqueenbee1579
# !$@%67

import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from sqlalchemy import create_engine


# --------------------------------------------- **BOT 1---------------------------------------------------------**

# check_credentials
def check_credentials(driver):
    try:
        driver.find_element("xpath",
                            "//p[contains(text(), 'Sorry, your password was incorrect. Please double-check your password.')]")
        present = False
        print("error")
    except Exception as e:
        present = True
    return present


# login
def login(driver, instahandle, instapassword, sleeptime):
    username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    username.clear()
    password.clear()
    username.send_keys(instahandle)
    password.send_keys(instapassword)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(sleeptime)
    return check_credentials(driver)


def skip_login_info(driver, sleeptime):
    # save your login info?
    time.sleep(sleeptime)
    notnow = driver.find_element(By.CSS_SELECTOR, "._ac8f>div")



# searchbox
def search(driver, instapage, sleeptime):
    time.sleep(sleeptime)
    searchbox = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
    searchbox.clear()
    searchbox.send_keys(instapage)
    time.sleep(sleeptime)
    # selects the item
    searchbox.send_keys(Keys.ENTER)
    time.sleep(sleeptime)
    # clicks enter
    searchbox.send_keys(Keys.ENTER)


def set_window_size(driver, sleeptime):
    time.sleep(sleeptime)
    a = driver.get_window_size()
    driver.set_window_size(a["width"], a["height"])


def scroller(driver, timeout, sleeptime):
    # scroll
    time.sleep(sleeptime)
    scrolldown = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    match = False
    while not match:
        last_count = scrolldown
        time.sleep(sleeptime)
        print(timeout, 'scroll time')
        scrolldown = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
        if last_count == scrolldown:
            match = True
        if timeout == 1:
            break
        else:
            timeout -= 1


def insta_posts(driver, sleeptime):
    posts = []
    links = driver.find_elements(By.TAG_NAME, 'a')
    for link in links:
        post = link.get_attribute('href')
        print(link)
        print(post)
        if '/p/' in post:
            posts.append(post)
    return posts


def getdata(driver, posts, sleeptime):
    raw_data = []
    for post in posts:
        print(f"Visiting page {post}")
        driver.get(post)
        time.sleep(sleeptime)
        shortcode = driver.current_url.split("/")[-2]
        selector = "ul._a9z6"
        try:
            if driver.find_element(By.CSS_SELECTOR, selector) is not None:
                content = driver.find_elements(By.CSS_SELECTOR, selector)
                for con in content:
                    html = con.get_attribute('innerHTML')
                    with open('dummy_sec.html', 'w', encoding="utf-8") as f:
                        f.write(html)
                    soup = BeautifulSoup(html, 'html.parser')

                    for link in soup.find_all('a'):
                        raw_data.append({
                            'tag': link.text,
                            'link': link.attrs.get('href'),
                            'page': soup.find('a').attrs.get('href'),
                            'date': soup.find('time').attrs.get('datetime'),
                            'img': soup.find('img').attrs.get('src')
                            # 'scraped_on': datetime.now(),
                        })
                    print(raw_data)
            else:
                print(f"{selector} not found")
        except Exception as e:
            print(e)
        finally:
            time.sleep(sleeptime)
    return raw_data


def covert_data_to_df(raw_data):
    df = pd.DataFrame(raw_data)
    new_dataframe = df[df['tag'].str.startswith('#')]
    sorted_df = new_dataframe.drop_duplicates().sort_values('tag')
    return sorted_df


def convert_df_to_csv(df):
    df.to_csv('hastags_rawdata1.csv', index=None, mode='a')
    print('Process Completed')



# ---------------------------------------------**BOT 2**-----------------------------------------

from datetime import datetime
import sqlite3
def save_dataframe(df: pd.DataFrame):
    val = datetime.now().strftime("_%d_%m_%y")
    print(val)
    engine = create_engine('sqlite:///hashtags.sqlite3', echo=False)
    out = df.to_sql(f'hashtag_{val}', con=engine, if_exists='append')
    print(f'total data added {out}')
    return val


# Adding posts Col to DB
def insertColPost(tableName):
    conn = sqlite3.connect('hashtags.sqlite3')
    cur = conn.cursor()
    doesExists = False
    res = cur.execute(f"""PRAGMA table_info({tableName})""").fetchall()
    for x in range(len(res)):
        if ('posts' in res[x]):
            doesExists = True
            break
    if (not doesExists):
        query = f"""ALTER TABLE {tableName} ADD COLUMN posts INTEGER"""
        cur.execute(query);
    conn.commit()
    conn.close()


# going to each hashtag page and extracting the number of posts
def tag_data(driver, row, sleeptime):
    try:
        time.sleep(sleeptime)
        prefix = 'https://www.instagram.com/' + row[2]
        driver.get(prefix)
        time.sleep(sleeptime)
        no_posts = driver.find_element(By.CLASS_NAME, "_ac2a")
        print(no_posts.text)
        return no_posts.text
    except Exception as e:
        print(e)


def readSqliteTable(tableName, driver, sleeptime):
    sqliteConnection = sqlite3.connect('hashtags.sqlite3')
    cursor = sqliteConnection.cursor()
    print("Connected to SQLite")
    counter = 0
    sqlite_select_query = f"""SELECT * from {tableName} ORDER BY tag ASC"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    sqliteConnection.close()
    print("Total rows are:  ", len(records))
    print("Printing each row")
    allqueries = ""
    for row in records:

        try:
            val = tag_data(driver, row, sleeptime + 1)
            sql_update_query = f"""Update {tableName} set posts = '{val}' where link= '{row[2]}';"""
            allqueries += sql_update_query
            print(sql_update_query)
        except Exception as e:
            print(e)
    conn = sqlite3.connect('hashtags.sqlite3')
    cursor = conn.cursor()
    cursor.executescript(allqueries)
    conn.commit()
    conn.close()
    print("Process Completed")


def sqlToDf(tableName):
    conn = sqlite3.connect('hashtags.sqlite3')
    sql_query = pd.read_sql_query(f''' SELECT * FROM {tableName}''', conn)
    df = pd.DataFrame(sql_query, columns=['tag', 'link', 'page', 'date', 'img', 'posts'])
    df['date'] = pd.to_datetime(df['date'])
    df['posts'] = df['posts'].replace(',', '', regex=True)
    df = df.replace('None', np.nan).dropna()
    df['posts'] = df['posts'].astype(float)
    df = df.dropna()
    return df

# -------------------------***Calling Functions***

# tableName=save_dataframe(dataframe)
# mdriver = webdriver.Chrome(ChromeDriverManager().install())
# insertColPost("hashtag_"+tableName)
# readSqliteTable("hashtag_"+tableName,mdriver,3)
