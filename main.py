#region Import Libraries

from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.chrome.options import Options
import csv
import string    
import random
import re

#endregion


app = FastAPI()


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()

    return driver


def find_text_data(driver, ext_type, ext_value, multi):

    if ext_type == "REGEX":

        source = driver.page_source

        pattern = r'{}'.format(ext_value)

        matches = re.findall(pattern, source, re.IGNORECASE)

        if multi == "True":

            return matches
        
        elif multi == "False":

            if len(matches) > 0:
                return matches[0]

            return matches

    # ===================================================================================================================

    if ext_type == "CLASS_NAME":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.CLASS_NAME, ext_value):

                list.append(item.text)
                

            return list

        elif multi == "False":

            if len(driver.find_elements(By.CLASS_NAME, ext_value)) > 0:
                return driver.find_elements(By.CLASS_NAME, ext_value)[0].text
                

    # ===================================================================================================================

    if ext_type == "XPATH":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.XPATH, ext_value):

                list.append(item.text)


            return list

        elif multi == "False":

            if len(driver.find_elements(By.XPATH, ext_value)) > 0:
                return driver.find_elements(By.XPATH, ext_value)[0].text
    
    # ===================================================================================================================

    if ext_type == "TAG_NAME":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.TAG_NAME, ext_value):
                list.append(item.text)

            return list

        if multi == "False":
            return driver.find_elements(By.TAG_NAME, ext_value)[0].text

    # ===================================================================================================================

    if ext_type == "CSS_SELECTOR":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.CSS_SELECTOR, ext_value):
                list.append(item.text)

            return list

        if multi == "False":
            return driver.find_elements(By.CSS_SELECTOR, ext_value)[1].text

    # ===================================================================================================================
        
    if ext_type == "ID":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.ID, ext_value):
                list.append(item.text)
            return list

        if multi == "False":
            if len(driver.find_elements(By.ID, ext_value)) > 0:
                return driver.find_elements(By.ID, ext_value)[0].text

    # ===================================================================================================================

    if ext_type == "LINK_TEXT":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.LINK_TEXT, ext_value):
                list.append(item.text)
            return list

        if multi == "False":
            if len(driver.find_elements(By.ID, ext_value)) > 0:
                return driver.find_elements(By.LINK_TEXT, ext_value)[0].text

    # ===================================================================================================================

    if ext_type == "NAME":

        if multi == "True":

            list = []

            for item in driver.find_elements(By.NAME, ext_value):
                list.append(item.text)
            return list

        if multi == "False":
            if len(driver.find_elements(By.ID, ext_value)) > 0:
                return driver.find_elements(By.NAME, ext_value)[0].text

    # ===================================================================================================================


# def create_csv(data):
    
#     filename = 'outputs/output'.join(random.choices(string.ascii_letters + string.digits, k = 10))

#     for url in data:
        
#         with open (filename, "a", newline = "") as csvfile:

#             for i in url :
#                 row_data = []

#                 pass

#             movies = csv.writer(csvfile)
#             test_list1.append(data)
#             movies.writerow(data)
#             test_list1.clear()
            
#         csvfile.close()


@app.post("/crawlin")
def crawl(body: dict):

    driver = create_driver()

    api_response_list = []

    urls = body["urls"]
    fields = body["fields"]

    for url in urls:

        driver.get(url)

        field_response_list = []

        for field in fields:
            
            if field["file"] == "False":

                def_response = find_text_data(driver,
                                        field["ext_type"],
                                        field["ext_value"],
                                        field["multi"],
                                        )
                
                name = field["name"]

                field_response = {
                    "name" : name,
                    "content" : def_response
                }

                field_response_list.append(field_response)
            
            else:
                #TODO
                pass
            
        response : dict = {
            "url" : url,
            "response" : field_response_list
        }

        api_response_list.append(response)

        # create_csv(api_response_list)

    return api_response_list












