import urllib3
import json

BOT_TOKEN = "7061481850:AAGuz2CbsdNOreTI-fV5UT18GQevE56HN3w"

def sendMessage(chat_id, text):
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = http.request("POST", url, fields=data)
    return json.loads(response.data.decode("utf-8"))

result = sendMessage(5918500544, "반갑습니다, 저는 용뇽이님이 만든 텔레그램 봇이랍니다 :)")