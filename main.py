from lxml import html
import requests
import time
import string
import random
import json


anycaptcha_API_key = ""

first_name = "Jhone"
last_name = "Kite"
dob_day = "25"
dob_month = "05"
dob_year = "1992"
password = "123456@asdf"


def randome_email(size=12, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))+"@gmail.com"

def randome_username(size=12, chars=string.ascii_lowercase + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

def anycaptcha_token_step_1(anycaptcha_API_key):
    data = {
    "clientKey": ""+anycaptcha_API_key+"",
    "task": {
        "type": "FunCaptchaTaskProxyless",
        "websitePublicKey": "E8A75615-1CBA-5DFF-8032-D16BCF234E10"
        }
    }
    headers = {"Content-Type":"application/json"}
    response = requests.post("https://api.anycaptcha.com/createTask", json=data, headers=headers)
    tree = json.loads(response.content)
    if tree['errorId']==0:
        return tree['taskId']        
    else:
        print(tree['errorDescription'])

def anycaptcha_token_step_2(anycaptcha_API_key,taskId):
    data = {
        "clientKey": ""+anycaptcha_API_key+"",
        "taskId": taskId
        }
    headers = {"Content-Type":"application/json"}
    response = requests.post("https://api.anycaptcha.com/getTaskResult", json=data, headers=headers)
    tree = json.loads(response.content)
    if tree['errorId']==0:
        if tree['status']=="ready":
            return tree['solution']['token']
        elif tree['status']=="processing":
            anycaptcha_token_step_2(anycaptcha_API_key,taskId)
    else:
        print(tree['errorDescription'])
    
def create_session_id():
    response = requests.get("https://account.battle.net/creation/flow/creation-full", allow_redirects=False)
    head = response.headers
    j_session = head['Set-Cookie']
    j_session = j_session.split("SESSION=")[1]
    j_session = j_session.split(";")[0]
    return j_session

def step_1(session_id):
    cookies = {"SESSION":""+session_id+""}
    response = requests.get("https://account.battle.net/creation/flow/creation-full", cookies=cookies)
    tree = html.fromstring(response.content)
    csrf = tree.xpath("//input[@id='flow-csrftoken']/@value")
    return csrf[0]

def step_2(dob_day,dob_month,dob_year,csrf_token,session_id,fun_token):
    cookies = {"SESSION":""+session_id+""}
    paramsPost = {"country":(None, "IND"),
                  "dob-day":(None, ""+dob_day+""),
                  "dob-plain":(None, ""),
                  "dob-month":(None, ""+dob_month+""),
                  "dob-year":(None, ""+dob_year+""),
                  "arkose":(None, ""+str(fun_token)+""),
                  "webdriver":(None, "false"),
                  "dob-format":(None, "DMY"),
                  "csrftoken":(None, ""+csrf_token+"")
                  }
    response = requests.post("https://account.battle.net/creation/flow/creation-full/step/get-started", files=paramsPost, cookies=cookies)

def step_3(first_name,last_name,csrf_token,session_id):
    cookies = {"SESSION":""+session_id+""}
    paramsPost = {"csrftoken":(None, ""+csrf_token+""),
                  "first-name":(None, ""+first_name+""),
                  "last-name":(None, ""+last_name+"")
                  }
    response = requests.post("https://account.battle.net/creation/flow/creation-full/step/provide-name", files=paramsPost, cookies=cookies)

def step_4(email,csrf_token,session_id):
    cookies = {"SESSION":""+session_id+""}
    paramsPost = {"phone-number":(None, ""),
                  "csrftoken":(None, ""+csrf_token+""),
                  "email":(None, ""+email+"")
                  }
    response = requests.post("https://account.battle.net/creation/flow/creation-full/step/provide-credentials", files=paramsPost, cookies=cookies)

def step_5(csrf_token,session_id):
    cookies = {"SESSION":""+session_id+""}
    paramsPost = (
        ("csrftoken", (None, ""+csrf_token+"")),
        ("opt-in-blizzard-news-special-offers", (None, "false")),
        ("tou-agreements-implicit", (None, "2c72a35c-bf1b-4ae6-99ec-80624e1b429c;208128")),
        ("tou-agreements-implicit", (None, "a4380ee5-5c8d-4e3b-83b7-ea26d01a9918;211090")),
        ("tou-agreements-implicit", (None, "none"))
        )
    response = requests.post("https://account.battle.net/creation/flow/creation-full/step/legal-and-opt-ins", files=paramsPost, cookies=cookies)

def step_6(password,csrf_token,session_id):
    cookies = {"SESSION":""+session_id+""}
    paramsPost = {"csrftoken":(None, ""+csrf_token+""),
                  "password":(None, ""+password+"")
                  }
    response = requests.post("https://account.battle.net/creation/flow/creation-full/step/set-password", files=paramsPost, cookies=cookies)
    
def step_7(username,csrf_token,session_id):
    cookies = {"SESSION":""+session_id+""}
    paramsPost = {"csrftoken":(None, ""+csrf_token+""),
                  "battletag":(None, ""+username+"")
                  }
    response = requests.post("https://account.battle.net/creation/flow/creation-full/step/set-battletag", files=paramsPost, cookies=cookies)
    tree = html.fromstring(response.content)
    if tree.xpath("//h1[@class='step__title step__block']/text()")[0]=="You're all set!":
        print("Account Generated Successfully")
        return 1
        

def main():
    email = randome_email()
    username = randome_username()
    session_id = create_session_id()
    csrf_token = step_1(session_id)
    taskId = anycaptcha_token_step_1(anycaptcha_API_key)
    fun_token = anycaptcha_token_step_2(anycaptcha_API_key,taskId)
    step_2(dob_day,dob_month,dob_year,csrf_token,session_id,fun_token)
    step_3(first_name,last_name,csrf_token,session_id)
    step_4(email,csrf_token,session_id)
    step_5(csrf_token,session_id)
    step_6(password,csrf_token,session_id)
    final_result = step_7(username,csrf_token,session_id)
    if final_result==1:
        print("User Name: ", username)
        print("Email: ", email)
        print("Pasword: ", password)
    else:
        print("Sorry!!!, Account NOT Generated")
    
main()
