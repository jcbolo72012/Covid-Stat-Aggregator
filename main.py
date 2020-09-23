from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tinydb import TinyDB, Query
from lxml import html
import requests
import urllib3
import os 
import time
import re

def run_webdriver(url): # scrapes url and returns covid data
    options = webdriver.ChromeOptions() 
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'chromedriver85.exe')
    driver = webdriver.Chrome(options=options, executable_path=filename)
    driver.get(url)
    
    time.sleep(10)
    kiddos = driver.find_elements_by_tag_name('rect')
    kiddos = [kid.get_attribute('aria-label') for kid in kiddos]
    for kid in kiddos:
        print(kid)
    return kiddos




def add_to_db(format, date, tests, db):  # add a column of data to the db
    Search = Query()
    if db.search((Search['date']==date) & (Search['type'] == format)) == []:
        db.insert({'date': date, 'type': format, 'tests': tests})

def connect_to_db(): # initialize connection to tinydb
    db = TinyDB('db.json')
    return db

def cycle(data, db): # cycles through each new bit of data and sends to db if new
    for item in data:
        if item != None:

            date = re.compile(r"\d+/\d+/\d\d").search(item)
            tests = re.compile(r"Tests ([\d,]+[.0+]?.)").search(item)
            if date and tests:
                date = date.group()
                
                tests=''.join([x for x in tests.group() if x in "0123456789.,"])

                print(tests)
                if data.index(item) < 8:
                    add_to_db("Student Negative", date, tests, db)
                if data.index(item) > 8 and data.index(item) < 15:
                    add_to_db("Student Positive", date, tests, db)
                if data.index(item) > 15 and data.index(item) < 23:
                    add_to_db("Faculty Negative", date, tests, db)
                if data.index(item) > 22 and data.index(item) < 30:
                    add_to_db("Faculty Positive", date, tests, db)
                if data.index(item) > 30 and "New Positive Tests" in item:
                    add_to_db("New Positive Overall", date, tests, db)


if __name__ == "__main__":
    data = run_webdriver("https://app.powerbi.com/view?r=eyJrIjoiMzI4OTBlMzgtODg5MC00OGEwLThlMDItNGJiNDdjMDU5ODhkIiwidCI6ImQ1N2QzMmNjLWMxMjEtNDg4Zi1iMDdiLWRmZTcwNTY4MGM3MSIsImMiOjN9")
    db = connect_to_db()
    cycle(data, db)
    print(db.all())