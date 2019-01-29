# -*- encoding:utf-8 -*-
import requests
import json

api_key = ''
secret_key = ''


def get_token():
    url = "https://openapi.baidu.com/oauth/2.0/token"
    grant_type = "client_credentials"
    data = {'grant_type': grant_type, 'client_id': api_key, 'client_secret': secret_key}
    r = requests.post(url, data=data)
    token = json.loads(r.text).get("access_token")
    return token


if __name__ == '__main__':
    with open('baidu.token', 'w', encoding='utf-8') as token_file:
        token = get_token()
        token_file.write(token)
