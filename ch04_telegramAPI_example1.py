import urllib3
import json

BOT_TOKEN = "7061481850:AAGuz2CbsdNOreTI-fV5UT18GQevE56HN3w"

def get_updates():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    return json.loads(response.data.decode("utf-8"))

updates = get_updates()
print(updates)