import urllib3
import json

BOT_TOKEN = "7061481850:AAGuz2CbsdNOreTI-fV5UT18GQevE56HN3w"

def sendPhoto(chat_id, image_url):
    data = {
        "chat_id": chat_id,
        "photo": image_url,
    }

    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = http.request("POST", url, fields=data)
    return json.loads(response.data.decode("utf-8"))

result = sendPhoto(5918500544, "https://logowik.com/standard-chartered-bank-new-2021-vector-logo-5417.html")
print(result)