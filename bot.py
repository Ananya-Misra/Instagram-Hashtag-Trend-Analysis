
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import sqlalchemy
from sqlalchemy import create_engine


#-----------------------------------------------BOT----------------------------------- 1
# login
def login(driver, instahandle, instapassword):
    username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    username.clear()
    password.clear()
    username.send_keys(instahandle)
    password.send_keys(instapassword)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)
    return True

def skip_login_info(driver):
    #save your login info?
    time.sleep(10)
    notnow = driver.find_element("xpath", "//button[contains(text(), 'Not Now')]").click()
def turn_off_notif(driver):
    #turn on notif
    time.sleep(10)
    notnow2 = driver.find_element("xpath", "//button[contains(text(), 'Not Now')]").click()

#searchbox
def search(driver, instapage):
    time.sleep(5)
    searchbox = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Search']")
    searchbox.clear()
    searchbox.send_keys(instapage)
    time.sleep(5)
    #selects the item
    searchbox.send_keys(Keys.ENTER);
    time.sleep(5)
    #clicks enter
    searchbox.send_keys(Keys.ENTER)

def set_window_size(driver):
    time.sleep(5)
    a=driver.get_window_size()
    driver.set_window_size(a["width"], a["height"])

def scroller(driver,timeout):
    #scroll
    time.sleep(5)
    scrolldown = driver.execute_script(
    "window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
    match = False
    while not match:
        last_count = scrolldown
        time.sleep(3)
        scrolldown = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
        if last_count == scrolldown:
            match = True
        if timeout == 0:
            break
        else:
            timeout-=1


def insta_posts(driver,limit=10):
    posts = []
    links = driver.find_elements(By.TAG_NAME, 'a')
    for link in links:
        post = link.get_attribute('href')
        print(link)
        print(post)
        print(limit)
        if limit==0:
            break;
        if '/p/' in post:
            posts.append(post)
            limit-=1;

    return posts

def getdata(driver,posts, page="",):
    raw_data = []
    for post in posts:
        print(f"Visiting page {post}")
        driver.get(post)
        time.sleep(5)
        shortcode = driver.current_url.split("/")[-2]
        selector = "ul._a9z6"
        try:
            if driver.find_element(By.CSS_SELECTOR, selector) is not None:
                content = driver.find_elements(By.CSS_SELECTOR, selector)
                for con in content:
                    html = con.get_attribute('innerHTML')
                    with open('dummy_sec.html', 'w',encoding="utf-8") as f:
                        f.write(html)
                    soup = BeautifulSoup(html,  'html.parser')

                    for link in soup.find_all('a'):
                        raw_data.append({
                            'tag':link.text,
                            'link':link.attrs.get('href'),
                            'page':soup.find('a').attrs.get('href'),
                            'date':soup.find('time').attrs.get('datetime'),
                            'img':soup.find('img').attrs.get('src')
                        })
                    print(raw_data)
            else:
                print(f"{selector} not found")
        except Exception as e:
            print(e)
        finally:
            time.sleep(5)
    return raw_data


def covert_data_to_df(raw_data):
    df = pd.DataFrame(raw_data)
    df[df['tag'].str.startswith('#')]
    return df

def convert_df_to_csv(df):
    df.to_csv('hastags_rawdata1.csv', index=None)
    print('Process Completed')

# **Calling functions**

#installing driver
mdriver = webdriver.Chrome(ChromeDriverManager().install())
mdriver.get("https://www.instagram.com/")
time.sleep(2)
insta_handle='twilightqueenbee1579'
insta_password='!$@%67'
insta_page='random_shotsbyme'
#if login successful
try:
    if login(mdriver,insta_handle,insta_password):
        print("Login successful")
        skip_login_info(mdriver)
        turn_off_notif(mdriver)
        mdriver.get("https://www.instagram.com/explore")
        set_window_size(mdriver)
        scroller(mdriver,0)
        time.sleep(3)
        fetched_posts=insta_posts(mdriver, 20)
        print(fetched_posts)
        print(f'len of posts {len(fetched_posts)}')
        fetched_data=getdata(mdriver,fetched_posts,insta_page)
        print("The time for fetched data has come...................=^^=")
        print(fetched_data)
        dataframe=covert_data_to_df(fetched_data)
        convert_df_to_csv(dataframe)
    else:
        print("Wrong credentials")
except Exception as e:
     print(e)




def mask_df(dataframe):
    mask = dataframe['tag'].str.contains('#', case=False, na=False)
    new_dataframe=dataframe[mask]
    new_dataframe = new_dataframe.drop_duplicates()
#converting the new dataframe to csv
# new_dataframe
sorted_df=new_dataframe.sort_values('tag')

convert_df_to_csv(sorted_df)
#----------------------------- BOT2 ---------------------------------------

from datetime import datetime

def save_dataframe(df:pd.DataFrame):
     val = datetime.now().strftime("_%d_%m_%y")
     print(val)
     engine = create_engine('sqlite:///hashtags.sqlite3', echo=False)
     df.to_sql(f'hashtag_{val}', con=engine, if_exists='append')
     return val;



#Adding posts Col to DB
import sqlite3
def insertColPost(tableName):
    conn = sqlite3.connect('hashtags.sqlite3')
    cur = conn.cursor()
    doesExists= False
    res=cur.execute(f"""PRAGMA table_info({tableName})""").fetchall()
    for x in range(len(res)):
      if('posts' in res[x]):

          doesExists=True
          break
    if(not doesExists):
        query=f"""ALTER TABLE {tableName} ADD COLUMN posts INTEGER"""
        cur.execute(query);
    conn.commit()
    conn.close()


# going to each hashtag page and extracting the number of posts
def tag_data(driver, row):
    try:
        time.sleep(3)
        prefix = 'https://www.instagram.com/' + row[2]
        driver.get(prefix)
        time.sleep(3)
        no_posts = driver.find_element(By.CLASS_NAME, "_ac2a")
        print(no_posts.text)
        return no_posts.text
    except Exception as e:
            print(e)
def readSqliteTable(tableName):
    sqliteConnection = sqlite3.connect('hashtags.sqlite3')
    cursor = sqliteConnection.cursor()
    print("Connected to SQLite")
    counter=0
    sqlite_select_query = f"""SELECT * from {tableName} ORDER BY tag ASC"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    sqliteConnection.close()
    print("Total rows are:  ", len(records))
    print("Printing each row")
    allqueries = ""
    for row in records:

        try:
            val = tag_data(mdriver, row)
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
 md
***Calling Functions***

tableName=save_dataframe(sorted_df)


print(tableName)

mdriver = webdriver.Chrome(ChromeDriverManager().install())
tableName="_05_03_23"
insertColPost("hashtag_"+tableName)


readSqliteTable("hashtag_"+tableName)

