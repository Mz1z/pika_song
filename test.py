import requests
import time

appid = "b3010d0000000000a0b9446579916119"
baseURL = "http://openapi.music.163.com/"


loginURL = "/openapi/music/basic/oauth2/login/anonymous"

r = requests.get(baseURL+loginURL+)
