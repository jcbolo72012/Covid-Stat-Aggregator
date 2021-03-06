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
from datetime import datetime
import re
import seaborn as sns
import pandas as pd


def run_webdriver(url, db): # scrapes url and returns covid data
    options = webdriver.ChromeOptions() 
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'chromedriver85.exe')
    driver = webdriver.Chrome(options=options, executable_path=filename)
    driver.get(url)
    
    time.sleep(10)
    kiddos = driver.find_elements_by_tag_name('rect')
    kiddos = [kid.get_attribute('aria-label') for kid in kiddos]

    # get the amount of students currently in isolation and total recovered

    current_in_isolation, total_recovered = 0, 0

    cards = driver.find_elements_by_class_name("cardItemContainer")
    
    for elem in cards:
        details = elem.find_element_by_class_name("details")

        # check if we have hit the 'in isolation' statistic
        if details.get_attribute('title') == "Currently in Isolation":
            current_in_isolation = elem.find_element_by_class_name("caption").get_attribute("title")
            now = datetime.now()
            # send this stat to the database with datestamp
            add_to_db("Current Isolation", now.strftime("%m/%d/%Y"), current_in_isolation, db)

        # check if we have hit the 'recovered' statistic
        if details.get_attribute('title') == "Recovered":
            total_recovered = elem.find_element_by_class_name("caption").get_attribute("title")
            now = datetime.now()
            # send this stat to the database with datestamp
            add_to_db("Recovered", now.strftime("%m/%d/%Y"), total_recovered, db)
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

def load_from_db(db):
        Search = Query()

        student_neg = [{x['date']: x['tests']} for x in db.search(Search['type']=="Student Negative")]  
        student_pos = [{x['date']: x['tests']} for x in db.search(Search['type']=="Student Positive")]  
        fac_neg = [{x['date']: x['tests']} for x in db.search(Search['type']=="Faculty Negative")]  
        fac_pos = [{x['date']: x['tests']} for x in db.search(Search['type']=="Faculty Positive")]  
        new_pos = [{x['date']: x['tests']} for x in db.search(Search['type']=="New Positive Overall")]  
        dates = [list(x.keys())[0] for x in student_neg]
        print(dates)
        stp = []
        fcp = []
        for date in dates:
            try:
                stp.append(student_pos[date])
        
        print(stp)
        inpv = input("STOP")


        data = {'Student Negative': [x[1] for x in student_neg],
                'Student Positive': [x[1] for x in student_pos],
                'Faculty Negative': [x[1] for x in fac_neg],
                'Faculty Positive': [x[1] for x in fac_pos],
                }
        print(dates)
        print(fac_neg)
        
        df = pd.DataFrame(data, columns = ['Student Negative', 'Student Positive', 'Faculty Negative', 'Faculty Positive'], index = [date for date in dates])
        return df

def plot_data(dataset):
    sns.set_theme()
    
    sns.relplot(
        data=dataset,
        x=dataset.Date, y=dataset.Tests
        
    )

if __name__ == "__main__":
    print("Connecting to db...")
    db = connect_to_db()
    # print("Scraping most recent statistics...")
    # data = run_webdriver("https://app.powerbi.com/view?r=eyJrIjoiMzI4OTBlMzgtODg5MC00OGEwLThlMDItNGJiNDdjMDU5ODhkIiwidCI6ImQ1N2QzMmNjLWMxMjEtNDg4Zi1iMDdiLWRmZTcwNTY4MGM3MSIsImMiOjN9", db)
    # cycle(data, db)
    print(str(len(db.all())), "objects in database!")

    #  pos_students = load_from_db(db)

    # TODO: Figure out a good way to load & display data
    print(pos_students)

    plot_data(pos_students)
    """ 
    Data Point type labels:
    
    Student Negative, 
    Student Positive, 
    Faculty Negative, 
    Faculty Positive, 
    New Positive Overall
    """