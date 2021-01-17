from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import json

def set_driver():
    with open('config/driver_window.json') as window:
        minimised = json.load(window).get('minimised')
    driver = webdriver.Chrome('config/chromedriver')
    if minimised:
        driver.minimize_window()
    else:
        driver.maximize_window()

    return driver

def get_job_description(url, descriptions_list):
    # Use selenium to try to access job full description.
    scraped_descriptions = descriptions_list
    driver = set_driver()
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
    jobs = driver.find_elements_by_class_name('jobsearch-SerpJobCard')

    def click_on_job_and_add_description(job_card):
        job_card.click()
        wait.until(EC.presence_of_element_located((By.ID, 'vjs-content')))
        scraped_descriptions.append(driver.find_element_by_id('vjs-content').text)

    for job in jobs:
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'jobsearch-SerpJobCard')))
        try:  # click on the job card and add its description to descriptions list
            click_on_job_and_add_description(job)
        except (ElementClickInterceptedException, TimeoutException):
            # if ElementClickInterceptedException, scroll away and try again
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            click_on_job_and_add_description(job)

    driver.close()
    driver.quit()
    return scraped_descriptions
