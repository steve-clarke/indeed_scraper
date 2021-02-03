import urllib
import requests
import os
import openpyxl
import selenium
import json
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from keyword_analyser import get_description_keywords
import string
import re
import math
import pprint

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException


def find_jobs():
    # parameters for search
    countrycode     = 'au'
    locality        = 'australia'
    queries         = ['graduate economist', # 12 jobs
                        'trainee economist', # 1 job, unrelated
                        'financial economist', # 19 jobs
                        'quantitative economist', #19 jobs
                        'economic researcher', # 43 jobs
                        'economic analyst', # 268 jobs
                        'econometrician', # 5 jobs
                        'behavioural economist', # 1 job
                        'economic forecaster', # 3 jobs
                        'macro economist', # 0 jobs
                        'pricing analyst', # 205 jobs
                        'regulatory economist', # 26 jobs
                        'macroeconomics'] # 31 jobs
    num_pages       = 1
    job_age         = 15 
    want_excel      = 'Y'

    query = ', '.join(queries)

    # construct URLs to be scraped, based on parameters above
    urls        = get_urls(countrycode, locality, query, num_pages, job_age)

    #jobs        = get_jobs(urls)

    #jobs_data, n_listings = extract_data(jobs, urls)
    #print('{} new job postings retrieved.'.format(n_listings))

    #get_description_keywords(jobs_data['descriptions'])

    # Option below to save recorded data to a spreadsheet:
    #if want_excel is 'Y':
        #save_to_excel(jobs_data, "results.xlsx")

def save_to_excel(jobs_data, filename):
    jobs = pd.DataFrame(jobs_data)
    jobs.to_excel(filename)


def get_urls(countrycode, locality, query, num_pages, job_age):
    # search URL for number of pages to be searched...
    url_variables   = {'q' : query,
                        'l' : locality,
                        'limit': 50
                        }
    url = ('https://' + countrycode + '.indeed.com/jobs?' + urllib.parse.urlencode(url_variables))
    print(url)
    start_from       = get_n_pages(url) * 50

    # aggregate URLs to be scraped...
    urls = []
    pages = np.arange(0, start_from, 50)
    for page in pages:
        url_variables   = {'q' : query,
                        'l' : locality,
                        'start': page,
                        'limit': 50
                        }
        url = ('https://' + countrycode + '.indeed.com/jobs?' + urllib.parse.urlencode(url_variables))
        urls.append(url)

    #print URLs to terminal
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(urls)

    return urls

def get_n_pages(url):
    page    = requests.get(url)
    soup    = BeautifulSoup(page.content, "html.parser")

    # get the number of jobs available from the search, and uses this to get number of pages to be searched
    n_jobs = str(soup.find(id="searchCountPages"))
    num = int(re.findall('\d+', n_jobs)[1])
    print('results: ' + str(num))
    pages = math.ceil(num / 50)
    print('pages: ' + str(pages))

    return pages


def get_jobs(urls): 
    jobs = None
    for url in urls:
        print('scanning {} ...'.format(url))
        page    = requests.get(url)
        soup    = BeautifulSoup(page.content, "html.parser")

        if jobs is not None:    # if 'jobs' exists, add to it
            jobs.append(soup.find(id="resultsCol"))
        else: # ...else, create it
            jobs = soup.find(id="resultsCol")

    return jobs


def extract_data(jobs, urls):
    job_elems = jobs.find_all('div', class_='jobsearch-SerpJobCard')
    
    cols            = []
    extracted_info  = []
    
    titles          = []
    companies       = []
    descriptions    = []

    cols.append('titles')
    for job_elem in job_elems:
        titles.append(get_query(job_elem))
    extracted_info.append(titles)

    cols.append('companies')
    for job_elem in job_elems:
        companies.append(get_company_name(job_elem))
    extracted_info.append(companies)

    cols.append('descriptions')
    for url in urls:
        descriptions = get_job_descriptions(url, descriptions)
    extracted_info.append(descriptions)
    
    jobs_data = {}
    
    for j in range(len(cols)):
        jobs_data[cols[j]] = extracted_info[j]
    
    n_listings = len(extracted_info[0])
    
    return jobs_data, n_listings


def get_query(job_elem) :
    title_elem  = job_elem.find('h2', class_='title')
    title       = title_elem.text.strip()
    return title


def get_company_name(job_elem) : 
    company_elem    = job_elem.find('div', class_='sjcl')
    company         = company_elem.text.strip()
    return company


# driver setup for job description crawler
# currently only supports Chrome 87.0.4280
def driver_setup():
    with open('config/driver_window.json') as window:
        minimised = json.load(window).get('minimised')
    driver = webdriver.Chrome('config/chromedriver')
    if minimised:
        driver.minimize_window()
    else:
        driver.maximize_window()

    return driver

def get_job_descriptions(url, descriptions):
    new_descriptions = descriptions
    driver = driver_setup()
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
    jobs = driver.find_elements_by_class_name('jobsearch-SerpJobCard')

    def click_on_job_and_add_description(job_card):
        job_card.click()
        wait.until(EC.presence_of_element_located((By.ID, 'vjs-content')))
        new_descriptions.append(set(str(driver.find_element_by_id('vjs-content').text).lower().replace('\n', ' ').translate(str.maketrans('', '', string.punctuation)).split(' ')))

    for job in jobs:
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
        try: 
            click_on_job_and_add_description(job)
        except (ElementClickInterceptedException, TimeoutException):
            # make another attempt after window scroll
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            click_on_job_and_add_description(job)

    driver.close()
    driver.quit()
    return new_descriptions

