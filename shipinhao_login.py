import json
import time

import requests
import os
import qrcode

def get_login_token(user_agent):
    request_url = "https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_login_code"

    headers = {
        'Origin': 'https://channels.weixin.qq.com',
        'Referer': 'https://channels.weixin.qq.com/platform/login-for-iframe?dark_mode=true&host_type=1',
        'User-Agent': user_agent,
        'Content-Type': 'application/json'
    }

    timestamp_ms = int(time.time() * 1000)
    request_data = {
        "timestamp": str(timestamp_ms),
        "_log_finder_uin": "",
        "_log_finder_id": "",
        "rawKeyBuff": None,
        "pluginSessionId": None,
        "scene": 7,
        "reqScene": 7
    }

    json_str = json.dumps(request_data)
    response = requests.post(request_url, headers=headers, data=json_str)
    jsonObj = response.json()
    return jsonObj['data']['token']


def check_login_status(user_agent, login_token):
    request_url = "https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_login_status"

    headers = {
        'Origin': 'https://channels.weixin.qq.com',
        'Referer': 'https://channels.weixin.qq.com/platform/login-for-iframe?dark_mode=true&host_type=1',
        'User-Agent': user_agent,
        'Content-Type': 'application/json'
    }

    while True:
        timestamp_ms = int(time.time() * 1000)
        request_params = {
            "token": login_token,
            "timestamp": str(timestamp_ms),
            "_log_finder_uin": "",
            "_log_finder_id": "",
            "scene": 7,
            "reqScene": 7
        }

        response = requests.post(request_url, headers=headers, params=request_params)
        jsonObj = response.json()
        print("login status: \n", jsonObj)
        status = jsonObj['data']['status']
        if status == 0:
            print("等待扫码...")
        elif status == 1:
            print("登录成功!")
            set_cookies = response.headers.get('Set-Cookie')
            cookie_str = str(set_cookies)
            return cookie_str
        elif status == 4:
            print("二维码已过期，请重新生成")
            break
        elif status == 5:
            print("已扫码，需要在手机上确认...")
        time.sleep(1)


def create_qr_code(login_token):
    url = "https://channels.weixin.qq.com/mobile/confirm_login.html?token=" + login_token
    qr = qrcode.QRCode(
        version=1,  # 控制QR码的大小（1为最小）
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # 容错率
        box_size=10,  # 每个“点”的像素大小
        border=4,  # 边框的宽度
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")
    img.save("shipinhao_qrcode.png")
    os.system("open shipinhao_qrcode.png")

def login(user_agent):
    login_token = get_login_token(user_agent)
    print("login_token: \n", login_token)

    create_qr_code(login_token)

    cookie_content = check_login_status(user_agent, login_token)
    print("cookie_content: \n", cookie_content)
    with open('shipinhao_cookie.txt', 'w', encoding='utf-8') as file:
        file.write(cookie_content)


if __name__ == '__main__':
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"

    login(user_agent)
