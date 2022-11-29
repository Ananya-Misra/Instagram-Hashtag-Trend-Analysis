# from instagram_data import scrape
# scrape("sandrathom11", "Pipelining48")

# from instascrape import *
# # Instantiate the scraper objects
# google = Profile('https://www.instagram.com/google/')
# google_post = Post('https://www.instagram.com/p/CG0UU3ylXnv/')
# google_hashtag = Hashtag('https://www.instagram.com/explore/tags/google/')
#
# # Scrape their respective data
# google.scrape()
# google_post.scrape()
# google_hashtag.scrape()
#
# print(google.followers)
# print(google_post['hashtags'])
# print(google_hashtag.amount_of_posts)

# from scrape_instagram import *
# response =instagram.profile_scraper(profile_link="https://www.instagram.com/aliaabhatt/")
# print(response)
# print(type(response))

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


def login(driver):
    username = driver.find_element(By.CSS_SELECTOR, "input[name='username']")
    password = driver.find_element(By.CSS_SELECTOR, "input[name='password']")
    username.clear()
    password.clear()
    username.send_keys("sandrathom11")
    password.send_keys("Pipelining48")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(5)
    return True


mdriver = webdriver.Chrome(ChromeDriverManager().install())
mdriver.get("https://www.instagram.com/")
time.sleep(2)
# login
if login(mdriver):
    print("Login successful")
