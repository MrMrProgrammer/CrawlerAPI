#region Import Libraries

from fastapi import FastAPI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import csv
import string    
import random
import re
import requests
from time import sleep
from fastapi.openapi.utils import get_openapi

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


def find_data(driver, name, action, file, ext_type, ext_value, multi, obj_type, inner_fields):

    if action == "extract" :

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
        
        else :
            
            list = []

            if file == "False":

                if multi == "True":

                    elements = driver.find_elements(EXTTYPE[ext_type], ext_value)

                    for element in elements:

                        if obj_type == "text":
                            list.append(element.text)

                        elif obj_type == "object":

                            if len(inner_fields) > 0:

                                for inner_field in inner_fields:
                            
                                    def_response = find_data(element,
                                                            inner_field["name"],
                                                            inner_field["action"],
                                                            inner_field["file"],
                                                            inner_field["ext_type"],
                                                            inner_field["ext_value"],
                                                            inner_field["multi"],
                                                            inner_field["obj_type"],
                                                            inner_field["inner_fields"],
                                                            )
                                    
                                    list.append(def_response)
                        
                        else:
                            list.append(element.get_attribute(obj_type))

                    return list

                elif multi == "False":

                    elements = driver.find_elements(EXTTYPE[ext_type], ext_value)

                    if len(elements) > 0:
                        element = elements[0]

                        if obj_type == "text":
                            list.append(element.text)
                            return list
                        
                        elif obj_type == "object":

                            if len(inner_fields) > 0:

                                for inner_field in inner_fields:
                            
                                    def_response = find_data(element,
                                                            inner_field["name"],
                                                            inner_field["action"],
                                                            inner_field["file"],
                                                            inner_field["ext_type"],
                                                            inner_field["ext_value"],
                                                            inner_field["multi"],
                                                            inner_field["obj_type"],
                                                            inner_field["inner_fields"],
                                                            )
                                    
                                    list.append(def_response)
                                    
                            else:
                                return []
                        
                            # return def_response

                        else:
                            list.append(element.get_attribute(obj_type))

                        return list

                    else:
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

                        downloaded_file = download_file(output, obj_type)

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

                        return download_file(output, obj_type)
                    
                    return list


    elif action == "sleep":
        sleep(int(obj_type))
        response = f"The process stopped for {obj_type} seconds."
        return [response]


    elif action == "click":
        btn = driver.find_elements(EXTTYPE[ext_type], ext_value)[0]
        btn.click()
        response = f"The desired button was clicked ({name})"
        return [response]
    

    elif action == "script":
        driver.execute_script(f"{obj_type}")
        response = "The page is scrolled to the desired location."
        return [response]


    elif action == "current_url":
        response = driver.current_url
        return [response]
    

    elif action == "input":
        input = driver.find_elements(EXTTYPE[ext_type], ext_value)[0]
        input.send_keys(obj_type)
        response = f"The '{obj_type}' value was entered in the desired input."
        return [response]
    

    elif action == "get_url":
        driver.get(obj_type)
        response = f"You have entered the '{obj_type}' link"
        return [response]
    
    elif action == "loop":
        for i in range(int(obj_type)):

            response = find_data(driver,
                                 name,
                                 action,
                                 file,
                                 ext_type,
                                 ext_value,
                                 multi,
                                 obj_type,
                                 inner_fields,
                                )
            
            return response


    else:
        response = "ERROR : The 'action' field value is not valid!"
        return response


def save_csv(data):

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

                movies = csv.writer(csvfile)
                movies.writerow(row_data)

    return file_name


def download_file(url, obj_type = None):
    
    response = requests.get(url)

    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k = 30))

    format = url.split('.')[-1]

    if obj_type != None:
        format = obj_type

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

        sleep(1.5)

        field_response_list = []

        for field in fields:

            def_response = find_data(driver,
                                     field["name"],
                                     field["action"],
                                     field["file"],
                                     field["ext_type"],
                                     field["ext_value"],
                                     field["multi"],
                                     field["obj_type"],
                                     field["inner_fields"],
                                    )
            
            name = field["name"]

            field_response = {
                "name" : name,
                "content" : def_response
            }

            print(field_response)

            if field["action"] == "extract" or field["action"] == "current_url" :
                field_response_list.append(field_response)

        path = save_csv(field_response_list)
            
        response : dict = {
            "url" : url,
            "file_path" : path,
            "response" : field_response_list
        }

        api_response_list.append(response)

    return api_response_list


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Web Crawler API",
        version="0.1.0",
        description="Using this api, you can crawl web pages and extract the data you want.",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema

    return app.openapi_schema

app.openapi = custom_openapi

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)