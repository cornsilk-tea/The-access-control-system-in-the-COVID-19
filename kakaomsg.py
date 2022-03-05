import json
import requests
import datetime
import os

REST_api = '06fdf8848e423adf43f9d98bc0057f6b'
code='KxP1LekGfddOxGsxHGgGb1hd1e0Kx6vUtGH9ZPN5Xh8WNt0rYFjqzi63Vg1xTox6CUeWxwo9dJkAAAF9qauoog'

def get_token():
    url = "https://kauth.kakao.com/oauth/token"

    data = {
        "grant_type" : "authorization_code",
        "client_id" : REST_api,
        "redirect_uri" : "https://localhost.com",
        "code" : code
    }

    response = requests.post(url, data=data)

    # 요청에 실패했다면,
    if response.status_code != 200:
        print("error! because ", response.json())
    else: # 성공했다면,
        tokens = response.json()
        return tokens

def token_set():
    def first_make_token():
        url = "https://kauth.kakao.com/oauth/token"

        data = {
            "grant_type" : "authorization_code",
            "client_id" : "06fdf8848e423adf43f9d98bc0057f6b",
            "redirect_uri" : "https://localhost.com",
            "code" : "sB2_0apPi4xmLYBgu8C8LOL2d4HlL9aq9nwoEWW0waVa-OxVCZ9LPHZblHt0D6NvNU3MnQorDKYAAAF9bKI0iQ"
        }

        response = requests.post(url, data=data)

        # 요청에 실패했다면,
        if response.status_code != 200:
            print("error! because ", response.json())
        else: # 성공했다면,
            tokens = response.json()
            print(tokens)
    # 카카오 토큰을 저장할 파일명
    KAKAO_TOKEN_FILENAME = "res/kakao_message/kakao_token.json"

    # 저장하는 함수
    def save_tokens(filename, tokens):
        with open(filename, "w") as fp:
            json.dump(tokens, fp)

    # 읽어오는 함수
    def load_tokens(filename):
        with open(filename) as fp:
            tokens = json.load(fp)

        return tokens

    # refresh_token으로 access_token 갱신하는 함수
    def update_tokens(app_key, filename) :
        tokens = load_tokens(filename)

        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type" : "refresh_token",
            "client_id" : REST_api,
            "refresh_token" : tokens['refresh_token']
        }
        response = requests.post(url, data=data)

        # 요청에 실패했다면,
        if response.status_code != 200:
            print("error! because ", response.json())
            tokens = None
        else: # 성공했다면,
            print(response.json())
            # 기존 파일 백업
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = filename+"."+ now
            os.rename(filename, backup_filename)
            # 갱신된 토큰 저장
            tokens['access_token'] = response.json()['access_token']
            save_tokens(filename, tokens)
            
        return tokens

    # 토큰 저장
    first_make_token
    # save_tokens(KAKAO_TOKEN_FILENAME, tokens) # 첫번째 토큰 저장

    # 토큰 업데이트 -> 토큰 저장 필수!
    # KAKAO_APP_KEY = "06fdf8848e423adf43f9d98bc0057f6b"
    # tokens = update_tokens(KAKAO_APP_KEY, KAKAO_TOKEN_FILENAME)
    # save_tokens(KAKAO_TOKEN_FILENAME, tokens) # 토큰 업데이트

"""
여기서부터는 카카오톡으로 메시지를 보내는 함수
"""
def send_msg(msg):
    # 읽어오는 함수
    def load_tokens(filename):
        with open(filename) as fp:
            tokens = json.load(fp)

        return tokens
    # 저장된 토큰 정보를 읽어 옴
    tokens = load_tokens("res/kakao_message/kakao_token.json")

    # 텍스트 메시지 url
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    # request parameter 설정
    headers = {
        "Authorization": "Bearer " + tokens['access_token']
    }

    data = {
        "template_object" : json.dumps({ "object_type" : "text",
                                        "text" : msg,
                                        "link" : {
                                            "web_url" : "https://skyhigh00v.ddns.net:5555/"
                                        }
                                        })
    }

    # 나에게 카카오톡 메시지 보내기 요청 (text)
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)

    # 요청에 실패했다면,
    if response.status_code != 200:
        print("error! because ", response.json())
    else: # 성공했다면,
        print('메시지를 성공적으로 보냈습니다.')