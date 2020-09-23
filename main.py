from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tinydb import TinyDB, Query
from lxml import html
import requests
import urllib3
import os 

def parentcycle(parent):
    children = parent.find_elements_by_xpath('.//*')
    for child in children:
        
        try:
            label = child.get_attribute('aria-label') # seek out elements with this label, they have info we care about!
            if not(label == None) and label[0:14]=="ResultLoadDate":
                print(label)
                print(child)
                inputvar = input(" ")
        except Exception as e:
            print("no <3")
            print(e)
        parentcycle(child)

def run_webdriver(url):
    options = webdriver.ChromeOptions() 
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'chromedriver85.exe')
    driver = webdriver.Chrome(options=options, executable_path=filename)
    driver.get(url)
    # WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.innerContainer")))
    parent = driver.find_element_by_xpath('//*[@id="reportLandingContainer"]/div/exploration-container')
    parentcycle(parent)
    driver.quit()


def add_to_db():  # add a column of data to the db
    return 0

def connect_to_db(): # initialize connection to tinydb
    db = TinyDB('db.json')
    return db

def scrape(soup):
    
    print(soup.a)
    whole_graph = soup.find("g", id="axisGraphicsContext")
    print(whole_graph)
    return 0

def get_the_soup(url):
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'html.parser')
    print(soup.body)

    return soup

if __name__ == "__main__":
    run_webdriver("https://app.powerbi.com/view?r=eyJrIjoiMzI4OTBlMzgtODg5MC00OGEwLThlMDItNGJiNDdjMDU5ODhkIiwidCI6ImQ1N2QzMmNjLWMxMjEtNDg4Zi1iMDdiLWRmZTcwNTY4MGM3MSIsImMiOjN9")
    # soup = get_the_soup("https://app.powerbi.com/view?r=eyJrIjoiMzI4OTBlMzgtODg5MC00OGEwLThlMDItNGJiNDdjMDU5ODhkIiwidCI6ImQ1N2QzMmNjLWMxMjEtNDg4Zi1iMDdiLWRmZTcwNTY4MGM3MSIsImMiOjN9") # https://www.bu.edu/healthway/community-dashboard/
    # scrape(soup)