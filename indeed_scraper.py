import urllib
import requests
import os
import openpyxl
import selenium
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

def find_jobs():
    countrycode     = input("Enter country prefix (eg. au, sg, hk): ")
    locality        = input("Enter locality: ")
    job_title       = input("Enter job title: ")
    num_pages       = input("Number of pages to be searched: ")

    urls        = get_urls(countrycode, locality, job_title, num_pages)
    jobs        = get_jobs(urls)
    jobs_data, n_listings   = extract_data(jobs)
    print('{} new job postings retrieved.'.format(n_listings))

    save_to_excel(jobs_data, "results.xlsx")

## -- save to excel -- ##
def save_to_excel(jobs_data, filename):
    jobs = pd.DataFrame(jobs_data)
    jobs.to_excel(filename)

def get_urls(countrycode, locality, job_title, num_pages):
    num_pages   = int(str(num_pages) + str('0'))

    urls = []

    pages = np.arange(0, num_pages, 10) # set the second argument to scan multiple pages. '10' defaults to first page only
    for page in pages:
        url_variables   = {'q' : job_title,
                        'l' : locality,
                        'fromage' : 'last',
                        'sort' : 'date', 
                        'start': page
                        }
        url = ('https://' + countrycode + '.indeed.com/jobs?' + urllib.parse.urlencode(url_variables))
        print(url)
        urls.append(url)

    print(*urls, sep='\n')
    return urls

## -- Get listing data and make a soup -- ##
def get_jobs(urls):

    for url in urls:

        print('scanning {} ...'.format(url))
        page    = requests.get(url)
        soup    = BeautifulSoup(page.content, "html.parser")

        try:    # if 'jobs' exists, add to it
            jobs.append(soup.find(id="resultsCol"))
        except NameError: # ...else, create it
            jobs = soup.find(id="resultsCol")

    return jobs

def extract_data(jobs):
    job_elems = jobs.find_all('div', class_='jobsearch-SerpJobCard')
    
    cols            = []
    extracted_info  = []
    
    titles          = []
    companies       = []

    cols.append('titles')
    for job_elem in job_elems:
        titles.append(get_job_title(job_elem))
    extracted_info.append(titles)

    cols.append('companies')
    for job_elem in job_elems:
        companies.append(get_company_name(job_elem))
    extracted_info.append(companies)
    
    jobs_list = {}
    
    for j in range(len(cols)):
        jobs_list[cols[j]] = extracted_info[j]
    
    n_listings = len(extracted_info[0])
    
    return jobs_list, n_listings

## --- functions for handling data --- ##
def get_job_title(job_elem) :
    title_elem  = job_elem.find('h2', class_='title')
    title       = title_elem.text.strip()
    return title

def get_company_name(job_elem) : 
    company_elem    = job_elem.find('div', class_='sjcl')
    company         = company_elem.text.strip()
    return company
