from flask import Flask, render_template, make_response, Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time, json

app = Flask(__name__)

@app.route("/")
def hello_world():
    rs = to_login()
    vcard_content = ""
    for contact in rs:
        vcard_content += f"""
BEGIN:VCARD
VERSION:3.0
FN:{contact['name']}
TEL;TYPE=CELL:{contact['phone']}
EMAIL:""
END:VCARD
"""
    

    # 파일 다운로드 응답
    response = Response(vcard_content, content_type="text/vcard")
    response.headers["Content-Disposition"] = "attachment; filename=contacts.vcf"
    return response


def get_id_pw() :
    with open('./secrets/settings.json') as json_file:
        return json.load(json_file)
    
def to_login() :
    login_info = get_id_pw()
    rs = []
    # 브라우저 드라이버 설정
    driver = webdriver.Chrome()

    # 로그인 페이지로 이동
    driver.get("https://login.office.hiworks.com/power21.co.kr")

    el = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div > main > div > div:nth-child(1) > form > fieldset > div.mb-5 > div > input"))
    )
    el.send_keys(login_info["id"])    
        
    button = driver.find_element(By.CSS_SELECTOR, "#root > div > main > div > div:nth-child(1) > form > fieldset > button")
    button.click()
    
    
    pw_input = WebDriverWait(driver, 10).until(        
        EC.presence_of_element_located((By.CSS_SELECTOR, "#root > div > main > div > div:nth-child(1) > form > fieldset > div.mantine-InputWrapper-root.mantine-TextInput-root.mb-5 > div > input"))
    )
    pw_input.send_keys(login_info["pw"])
    
    
    login_btn = driver.find_element(By.CSS_SELECTOR, "#root > div > main > div > div:nth-child(1) > form > fieldset > button")
    login_btn.click()
    
    
    #근무경비처리
    work_money_process = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#contents > div.header-wrapper > div > div > div > div:nth-child(6) > a"))
    )
    work_money_process.click()
    
    
    #임직원 정보
    worker_info = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,"#app > div:nth-child(3) > div.split-wrap > div.split-item.left > div > div.vb.vb-invisible > div.vb-content > nav > a:nth-child(2)"))
    )
    worker_info.click()
    
    conatiner = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,"#org-members"))
    )
    
    dl_elements = conatiner.find_elements(By.TAG_NAME, "dl")  # 하위 dl 태그들 찾기
    for dl_element in dl_elements :
        item = {"name" : "", "phone" : ""}
        wait_for_popup_close = WebDriverWait(driver, 10).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "#insa_info_layer"))
        )
        
        dl_element.click()
        
        wait_for_popup_display = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#insa_info_layer"))
        )
        
        name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#insa_info_layer > div.userView.insa-layer > div.proflie_right > dl > dd.insa-layer-name"))
        )
        name = name.get_attribute("innerHTML")
        
        info_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,"#insa_info_layer > div.userView.insa-layer > dl"))
        )
        info_titles = info_container.find_elements(By.TAG_NAME, "span")
        for info_title in info_titles :
            if info_title.get_attribute("innerHTML") == "휴대전화" :
                phone_number_container = info_title.find_element(By.XPATH, "..").find_element(By.XPATH, "following-sibling::*")
                phone_number = phone_number_container.find_element(By.TAG_NAME, "span").get_attribute("innerHTML")
                print(phone_number)
                item["phone"] = phone_number
                break

        item["name"] = "빡빡 " + name
        driver.find_element(By.CSS_SELECTOR, "#insa_info_layer > a").click()
        
        rs.append(item)
        
    
    # 브라우저 종료
    driver.quit()
    
    return rs
if __name__ == "__main__" :
    app.run(host="192.168.0.2",port=5001, debug=True)