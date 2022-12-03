import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

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

#login_info
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

#for scrolling
def scroller(driver):
    #scroll
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

# to get the instagram posts
def insta_posts(driver):
    posts = []
    links = driver.find_elements(By.TAG_NAME, 'a')
    for link in links:
        post = link.get_attribute('href')
        if '/p/' in post:
            posts.append(post)
    return posts

# to get the instagram post details
def getdata(driver,posts, page=""):
    raw_data = []
    for post in posts:
        driver.get(post)
        time.sleep(7)
        shortcode = driver.current_url.split("/")[-2]
        print("shortcode", shortcode)
        selector = "div._aa06"
        # print("selector", selector)
        if driver.find_element(By.CSS_SELECTOR, selector) is not None:
            content = driver.find_elements(By.CSS_SELECTOR, selector)
            for con in content:
                html = con.get_attribute('innerHTML')
                with open('dummy_sec.html', 'w',encoding="utf-8") as f:
                    f.write(html)
                soup = BeautifulSoup(html,  'html.parser')
                # print(soup)
                for link in soup.find_all('a'):
                    # print(link)
                    raw_data.append({
                        'tag':link.text,
                        'link':link.attrs.get('href'),
                        'page':page,
                        'date':soup.find('time').attrs.get('datetime')
                    })
        else:
            print("not found")
            time.sleep(5)
        return raw_data


# to convert data to dataframe
def covert_data_to_df(raw_data):
    df = pd.DataFrame(raw_data)
    df[df['tag'].str.startswith('#')]
    return df

# to convert dataframe to csv
def convert_df_to_csv(df):
    df.to_csv('hastags_rawdata1.csv', index=None)
    print('Process Completed')