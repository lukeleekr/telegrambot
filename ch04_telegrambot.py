### 기본 정보 설정 단계 ###
import urllib3
import json
import openai
from fastapi import Request, FastAPI

# OpenAI API Key
API_KEY = "### YOUR OPENAI API KEY ###"
openai.api_key = API_KEY

# Telegram Bot Token
BOT_TOKEN = "7061481850:AAGuz2CbsdNOreTI-fV5UT18GQevE56HN3w"


### 기능 함수 구현 단계 ###
# 메시지 전송 함수
def sendMessage(chat_id, text, msg_id):
    data = {
        "chat_id": chat_id,
        "text": text,
        "reply_to_message_id": msg_id,
    }

    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = http.request("POST", url, fields=data)
    return json.loads(response.data.decode("utf-8"))

# 사진 전송 함수
def sendPhoto(chat_id, image_url, msg_id):
    data = {
        "chat_id": chat_id,
        "photo": image_url,
        "reply_to_message_id": msg_id,
    }

    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    response = http.request("POST", url, fields=data)
    return json.loads(response.data.decode("utf-8"))

# Initialize a global dictionary to store conversation histories
conversation_histories = {}

# ChatGPT에게 질문/답변 받기
def getTextFromGPT(chat_id, new_message):
    # Ensure the chat has an entry in the conversation history
    if chat_id not in conversation_histories:
        conversation_histories[chat_id] = [{"role": "system", "content": "You are a thoughtful assistant."}]
    
    # Append the new user message to the conversation history
    conversation_histories[chat_id].append({"role": "user", "content": new_message})
    
    # Generate response using the updated conversation history
    response = openai.chat.completions.create(
        model="gpt-4-0125-preview",
        messages=conversation_histories[chat_id],
        temperature=0.9,
        
    )
    
    # Assume the API response appends the system's latest message to the history
    system_message = response.choices[-1].message
    
    # Optionally, you can store the system response in your history too, if needed
    
    return system_message.content


# DALL.E 3에게 질문/그림 URL 받기
def getImageURLFromDALLE(messages):
    response = openai.images.generate(
    prompt = messages,
    n = 1,
    size = "512x512",
)
    image_url = response.data[0].url
    return image_url

# 서버 생성 단계
app = FastAPI()

@app.get("/")
async def root():
    #return {"message": "TelegramChatbot"}
    return 0

@app.post("/gpt/")
async def chat(request: Request):
    telegramrequest = await request.json()
    chatBot(telegramrequest)
    #return {"message": "TelegramChatbot/gpt"}
    return 0

### 메인 함수 구현 단계 ###
def chatBot(telegramrequest):
    result = telegramrequest
    if not result['message']['from']['is_bot']:
        # 메시지를 보낸 사람의 chat id
        chat_id = str(result['message']['chat']['id'])
        # 해당 메시지의 id
        msg_id = str(int(result['message']['message_id']))
        # 해당 메시지의 본문
        message_text = result['message']['text']

        # 그림 생성을 요청했다면
        if '/img' in result ['message']['text']:
            prompt = result['message']['text'].replace('/img', '')
            # DALL.E 3로부터 생성한 이미지 URL 받기
            bot_response = getImageURLFromDALLE(prompt)
            # 이미지를 텔레그램 방으로 보내기
            sendPhoto(chat_id, bot_response, msg_id)
        
        # ChatGPT의 답변을 요청했다면
        else:
            # Treat all other messages as ChatGPT prompts
            # No need to replace '/ask', handle the text directly
            bot_response = getTextFromGPT(chat_id, message_text)  # Ensure getTextFromGPT is updated to handle chat_id
            sendMessage(chat_id, bot_response, msg_id)
    return 0