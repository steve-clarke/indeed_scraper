from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException, NoSuchElementException
import json

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
        new_descriptions.append(driver.find_element_by_id('vjs-content').text)

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
