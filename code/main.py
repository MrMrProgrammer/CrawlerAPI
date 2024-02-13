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
import requests

#endregion


EXTTYPE = {
    "CLASS_NAME" : By.CLASS_NAME,
    "XPATH" : By.XPATH,
    "TAG_NAME" : By.TAG_NAME,
    "CSS_SELECTOR" : By.CSS_SELECTOR,
    "ID" : By.ID,
    "LINK_TEXT" : By.LINK_TEXT,
    "NAME" : By.NAME,
}


app = FastAPI()


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    # , options=chrome_options
    driver.maximize_window()

    return driver


def find_text_data(driver, file, ext_type, ext_value, multi):

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
    
    list = []

    if file == "False":

        if multi == "True":

            for item in driver.find_elements(EXTTYPE[ext_type], ext_value):

                list.append(item.text)

            return list

        elif multi == "False":

            if len(driver.find_elements(EXTTYPE[ext_type], ext_value)) > 0:

                list.append(driver.find_elements(EXTTYPE[ext_type], ext_value)[0].text)

                return list
            
            return list
        
    elif file == "True":

        if multi == "True":

            for item in driver.find_elements(EXTTYPE[ext_type], ext_value):

                item_href = item.get_attribute('href')
                item_src = item.get_attribute('src')

                if item_href != None:
                    output = item_href
                
                elif item_src != None:
                    output = item_src
                
                else:
                    output = None

                downloaded_file = download_file(output)

                list.append(downloaded_file)

            return list

        elif multi == "False":

            item = driver.find_elements(EXTTYPE[ext_type], ext_value)

            if len(item) > 0:

                item_href = item[0].get_attribute('href')
                item_src = item[0].get_attribute('src')

                if item_href != None:
                    output = item_href
                
                elif item_src != None:
                    output = item_src

                return download_file(output)
            
            return list


def save_csv(data, url):

    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k = 30))

    file_name = "../outputs/csv/" + random_string + ".csv"

    with open(file_name, "a", newline="") as csvfile:

        for field in data:

            field_name = field["name"]

            contents = field["content"]

            if contents == None :
                return None

            for content in contents:

                row_data = []

                row_data.append(field_name)
                row_data.append(content)
                row_data.append(url)

                movies = csv.writer(csvfile)
                movies.writerow(row_data)

    return file_name


def download_file(url):
    
    response = requests.get(url)

    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k = 30))

    format = url.split('.')[-1]

    file_name = "../outputs/file/" + random_string + "." + format
    
    if response.status_code == 200:
        
        with open(file_name, 'wb') as f:

            f.write(response.content)

        print("فایل با موفقیت دانلود شد!")

    else:
        print("خطا در دانلود فایل:", response.status_code)

    return file_name


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

            def_response = find_text_data(driver,
                                    field["file"],
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

        path = save_csv(field_response_list, url)
            
        response : dict = {
            "url" : url,
            "file_path" : path,
            "response" : field_response_list
        }

        api_response_list.append(response)

        # create_csv(api_response_list)

    return api_response_list
