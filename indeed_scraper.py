import urllib
import requests
import os
import openpyxl
import selenium
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from web_extension import get_job_description

def find_jobs():
    job_title = input("Enter job title: ")
    location = input("Enter location: ")

    jobs, url               = scan_listings(job_title, location)
    jobs_list, n_listings   = extract_job_information(jobs, url)
    print('{} new job postings retrieved.'.format(n_listings))

    save_jobs_to_excel(jobs_list, "results.xlsx")

## -- save to excel -- ##
def save_jobs_to_excel(jobs_list, filename):
    jobs = pd.DataFrame(jobs_list)
    jobs.to_excel(filename)

## -- Get listing data and make a soup -- ##
def scan_listings(job_title, location):
    job_title   = job_title.replace(" ", "+")

    print(job_title)
    print(location)

    pages = np.arange(0, 10, 10) # set the second argument to scan multiple pages. '10' defaults to first page only
    for page in pages:
        url_variables   = {'q' : job_title,
                        'l' : location,
                        'fromage' : 'last',
                        'sort' : 'date', 
                        'start': page
                        }

        url     = ('https://au.indeed.com/jobs?' + urllib.parse.urlencode(url_variables))

        print('scanning {} ...'.format(url))
        page    = requests.get(url)
        soup    = BeautifulSoup(page.content, "html.parser")

        try:    
            jobs.append(soup.find(id="resultsCol"))
        except NameError:
            jobs = soup.find(id="resultsCol")

    return jobs, url

## --- functions for handling data --- ##
def get_job_title(job_elem) :
    title_elem  = job_elem.find('h2', class_='title')
    title       = title_elem.text.strip()
    return title

def get_company_name(job_elem) : 
    company_elem    = job_elem.find('div', class_='sjcl')
    company         = company_elem.text.strip()
    return company

## --- extract data --- ##
def extract_job_information(jobs, url):
    job_elems = jobs.find_all('div', class_='jobsearch-SerpJobCard')
    
    cols            = []
    extracted_info  = []
    
    titles          = []
    companies       = []
    descriptions    = []

    cols.append('titles')
    for job_elem in job_elems:
        titles.append(get_job_title(job_elem))
    extracted_info.append(titles)

    cols.append('companies')
    for job_elem in job_elems:
        companies.append(get_company_name(job_elem))
    extracted_info.append(companies)

    cols.append('descriptions')
    descriptions = get_job_description(url, descriptions)
    extracted_info.append(descriptions)
    
    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    n_listings = len(extracted_info[0])
    
    return jobs_list, n_listings
