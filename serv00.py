import os
import re
import json
import time
import pytz
import string
import random
import ddddocr
import inspect
import hashlib
import requests
from faker import Faker
from loguru import logger
from datetime import datetime
from urllib.parse import quote
from fake_headers import Headers
from urllib.parse import urlencode
from requests.exceptions import JSONDecodeError

os.makedirs("static", exist_ok=True)
config_file = 'static/config.json'


def get_user_name():
    url = "https://www.ivtool.com/random-name-generater/uinames/api/index.php?region=united%20states&gender=male&amount=5&="
    resp = requests.get(url, verify=False)
    if resp.status_code != 200:
        print(resp.status_code, resp.text)
        raise Exception("获取名字出错")
    data = resp.json()
    return data


def generate_random_username():
    length = random.randint(7, 10)
    characters = string.ascii_letters
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


def generate_random_email(domain):
    length = random.randint(7, 10)
    characters = string.ascii_lowercase + string.digits
    username = ''.join(random.choice(characters) for _ in range(length))
    return f"{username}@{domain}"


def generate_random_headers():
    return {
        "Accept-Language": random.choice(["en-US,en;q=0.9", "ja-JP,ja;q=0.9", "fr-FR,fr;q=0.9", "de-DE,de;q=0.9", "es-ES,es;q=0.9"]),
        "User-Agent": Headers(os="random").generate()["User-Agent"],
        "X-Forwarded-For": Faker().ipv4(),
        "X-Network-Type": random.choice(["Wi-Fi", "4G", "5G"]),
        "X-Timezone": random.choice(pytz.all_timezones)
    }


def generate_random_data():
    screen_resolution = f"{random.choice([1280, 1366, 1440, 1600, 1920])}x{random.choice([720, 768, 900, 1080, 1200])}"
    fonts = ["Arial", "Times New Roman", "Verdana", "Helvetica", "Georgia", "Courier New"]
    webgl_info = {
        "vendor": random.choice(["Google Inc. (NVIDIA)", "Intel Inc.", "AMD Inc."]),
        "renderer": random.choice([
            "ANGLE (NVIDIA, NVIDIA GeForce GTX 1080 Direct3D11 vs_5_0 ps_5_0, D3D11)", "Intel(R) HD Graphics 630",
            "AMD Radeon RX 580", "NVIDIA GeForce RTX 3090", "Intel(R) Iris Plus Graphics 655",
            "AMD Radeon RX 5700 XT", "NVIDIA GeForce GTX 1660 Ti",
            "Intel(R) UHD Graphics 630 (Coffeelake)", "AMD Radeon RX 5600 XT",
            "NVIDIA Quadro RTX 8000", "Intel(R) HD Graphics 520",
            "AMD Radeon RX 480", "NVIDIA GeForce GTX 1050 Ti", "Intel(R) UHD Graphics 620", "NVIDIA GeForce RTX 3080", "AMD Radeon Vega 64",
            "NVIDIA Titan V", "AMD Radeon RX 6800 XT", "NVIDIA GeForce GTX 980 Ti", "Intel(R) Iris Xe Graphics"
        ])
    }
    return {
        "screen_resolution": screen_resolution,
        "color_depth": random.choice([16, 24, 32]),
        "fonts": random.sample(fonts, k=random.randint(3, len(fonts))),
        "webgl_info": webgl_info,
        "canvas_fingerprint": hashlib.md5(os.urandom(16)).hexdigest(),
        "plugins": random.sample(["Chrome PDF Viewer", "Google Docs Offline", "AdBlock", "Grammarly", "LastPass"], k=random.randint(2, 5))
    }



def start_task(email_domains, num_emails):
    captcha_retry_limit = 5
    for domain in email_domains:
        for _ in range(num_emails):
            id_retry = 1
            while True:
                try:
                    email = generate_random_email(domain)
                    random_headers = generate_random_headers()
                    random_data = generate_random_data()
                    User_Agent = random_headers["User-Agent"]
                    Cookie = "csrftoken={}"
                    url1 = "https://www.serv00.com/offer/create_new_account"
                    headers = {"User-Agent": User_Agent, **random_headers}
                    captcha_url = "https://www.serv00.com/captcha/image/{}/"
                    header2 = {"Cookie": Cookie, "User-Agent": User_Agent, **random_headers}
                    url3 = "https://www.serv00.com/offer/create_new_account.json"
                    header3 = {
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Referer": "https://www.serv00.com/offer/create_new_account",
                        "Cookie": Cookie,
                        "User-Agent": User_Agent,
                        **random_headers
                    }

                    usernames = get_user_name()
                    _ = usernames.pop()
                    first_name = _["name"]
                    last_name = _["surname"]
                    username = generate_random_username().lower()
                    print(""), logger.info(f"{email} {first_name} {last_name} {username}")
                    with requests.Session() as session:
                        logger.info(f"获取网页信息 - 尝试次数: \033[1;94m{id_retry}\033[0m.")
                        resp = session.get(url=url1, headers=headers, verify=False)
                        headers = resp.headers
                        content = resp.text
                        csrftoken = re.findall(r"csrftoken=(\w+);", headers.get("set-cookie"))[0]
                        header2["Cookie"] = header2["Cookie"].format(csrftoken)
                        header3["Cookie"] = header3["Cookie"].format(csrftoken)
                        captcha_0 = re.findall(r'id=\"id_captcha_0\" name=\"captcha_0\" value=\"(\w+)\">', content)[0]
                        captcha_retry = 1

                        while True:
                            time.sleep(random.uniform(0.5, 1.2))
                            logger.info("获取验证码")
                            resp = session.get(url=captcha_url.format(captcha_0), headers=dict(header2, **{"Cookie": header2["Cookie"].format(csrftoken)}), verify=False)
                            time.sleep(random.uniform(0.5, 2))
                            content = resp.content
                            with open("static/image.jpg", "wb") as f:
                                f.write(content)
                            captcha_1 = ddddocr.DdddOcr(show_ad=False).classification(content).upper()
                            if bool(re.match(r'^[a-zA-Z0-9]{4}$', captcha_1)):
                                logger.info(f"识别验证码成功: \033[1;92m{captcha_1}\033[0m")
                                break
                            else:
                                logger.warning("\033[7m验证码识别失败,正在重试...\033[0m")
                                captcha_retry += 1
                                if captcha_retry > captcha_retry_limit:
                                    logger.error("验证码识别失败次数过多,退出重试.")
                                    return
                                continue

                        data = f"csrfmiddlewaretoken={csrftoken}&first_name={first_name}&last_name={last_name}&username={username}&email={quote(email)}&captcha_0={captcha_0}&captcha_1={captcha_1}&question=free&tos=on{urlencode(random_data)}"
                        time.sleep(random.uniform(0.5, 1.2))
                        logger.info("请求信息")
                        resp = session.post(url=url3, headers=dict(header3, **{"Cookie": header3["Cookie"].format(csrftoken)}), data=data, verify=False)
                        logger.info(f'请求状态码: \033[1;93m{resp.status_code}\033[0m')
                        try:
                            content = resp.json()
                            if resp.status_code == 200 and len(content.keys()) == 2:
                                logger.success(f"\033[1;92m🎉 账户 {username} 已成功创建!\033[0m")
                                break
                            else:
                                first_key = next(key for key in content if key not in ['__captcha_key', '__captcha_image_src'])
                                first_content = re.search(r"\['(.+?)'\]", str(content[first_key])).group(1)
                                logger.info(f"\033[36m{first_key.capitalize()}: {first_content}\033[0m")
                                if first_content == "An account has already been registered to this e-mail address.":
                                    logger.warning(f"\033[1;92m该邮箱已存在,或账户 {username} 已成功创建🎉!")
                                    break
                        except JSONDecodeError:
                            logger.error("\033[7m获取信息错误,正在重试...\033[0m")
                            time.sleep(random.uniform(0.5, 1.2))
                            continue
                        if content.get("captcha") and content["captcha"][0] == "Invalid CAPTCHA":
                            captcha_0 = content["__captcha_key"]
                            logger.warning("\033[7m验证码错误,正在重新获取...\033[0m")
                            time.sleep(random.uniform(0.5, 1.2))
                            continue
                        if content.get("username") and content["username"][0] == "Maintenance time. Try again later.":
                            id_retry += 1
                            logger.error("\033[7m系统维护中,正在重试...\033[0m")
                            time.sleep(random.uniform(0.5, 1.2))
                            break
                        if content.get("email") and content["email"][0] == "Enter a valid email address.":
                            logger.error("\033[7m无效的邮箱,请重新输入.\033[0m")
                            time.sleep(random.uniform(0.5, 1.2))
                            return
                        else:
                            return
                except Exception as e:
                    logger.error(f"\033[7m发生异常:{e},正在重新开始任务...\033[0m")
                    time.sleep(random.uniform(0.5, 1.2))


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    resp = requests.get("https://www.serv00.com/", verify=False)
    response = requests.get('https://ping0.cc/geo', verify=False)
    print(f"=============================\n\033[96m{response.text[:200]}\033[0m=============================")
    match = re.search(r'(\d+)\s*/\s*(\d+)', resp.text).group(0).replace(' ', '') if resp.status_code == 200 and re.search(r'(\d+)\s*/\s*(\d+)', resp.text) else (logger.error('请求失败,请检查代理IP是否封禁!'), exit())
    logger.info(f"\033[1;5;32m当前注册量:{match}\033[0m")

    email_domains_str = os.environ.get("EMAIL_DOMAIN", "aaedu.edu.pl")
    email_domains = [domain.strip() for domain in email_domains_str.split(';')]

    num_emails = int(os.environ.get("NUM_EMAILS", 1000000000))

    start_task(email_domains, num_emails)
