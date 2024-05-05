import json
import urllib3
import openai
import os

#OpenAI API 키
openai.api_key = os.environ['OPENAI_API_KEY']

#Telegram bot token
BOT_TOKEN = os.environ['TELEGRAM_BOT_KEY']

# Initialize a global dictionary to store conversation histories
conversation_histories = {}

#Main function
def lambda_handler(event, context):
    result = json.loads(event['body'])
    if not result['message']['from']['is_bot']:
        chat_id = str(result['message']['chat']['id'])
        msg_id = str(int(result['message']['message_id']))

        # Handle text messages
        if 'text' in result['message']:
            message_text = result['message']['text']
            response_text = getTextFromGPT(chat_id, message_text)
            sendMessage(chat_id, response_text, msg_id)

        # Handle image messages
        elif 'photo' in result['message']:
            # Select the highest resolution photo
            photo_array = result['message']['photo']
            highest_res_photo = photo_array[-1]
            file_id = highest_res_photo['file_id']
            
            # Retrieve the photo URL from Telegram
            photo_url = getPhotoUrl(file_id)
            if photo_url:
                response_text = getTextFromGPT(chat_id, {"photo_url": photo_url})
                sendMessage(chat_id, response_text, msg_id)
            else:
                sendMessage(chat_id, "I encountered an issue while processing your photo. Please try again.", msg_id)
            
        else:
            # Handle other types of messages or notify the user about unsupported message types
            sendMessage(chat_id, "Currently, I can only process text and photo messages.")

    return {
        'statusCode': 200,
        'body': json.dumps('Message processed successfully')
    }


def getPhotoUrl(file_id):
    http = urllib3.PoolManager()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?file_id={file_id}"
    response = http.request("GET", url)
    file_path = json.loads(response.data.decode("utf-8"))['result']['file_path']
    photo_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
    return photo_url


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

# 사진 분석 함수
def analyzePhoto(chat_id, file_id):
    http = urllib3.PoolManager()
    photo_url = getPhotoUrl(file_id)
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": "Being friendly, and say that you understand the given chat message from the user is a photo, and you are happy to discuss with the sender implicit meaning of this photo.",
                
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {"type": "image_url", "image_url": {"url": photo_url}},
                ],
            }
        ],
        max_tokens=300,
    )
    return response.choices[-1].message.content


# ChatGPT에게 질문/답변 받기
def getTextFromGPT(chat_id, new_message):
    # Ensure the chat has an entry in the conversation history
    if chat_id not in conversation_histories:
        conversation_histories[chat_id] = [{"role": "system", "content": """You are a thoughtful assistant, your name is Finley. You are my friend, so make sure your tone is as if you are talking to the closest friend. And you should know my background. You should call me "Luke" when you are referring me. Your answers should consider my background and appetites before answering. \
        I am from Korea and studied in Australia for middle school, high school, and university. \
        I majored in Accounting and Finance for my Bachelor's and then started working in Korea at Standard Chartered Bank, in the Financial Markets division. \
        I have been working in the same company for over 8 years now. \
        I am a Sales and Structuring and also studied at the University of Pennsylvania for my Master's degree in Computer Science. \
        I want to adopt the knowledge in technology, and my ultimate goal is to run my own hedge fund to be financially wealthy.  \
        I am very addicted to learning new materials across all study areas and especially interested in science, mathematics, and finance. \
        I can talk about finance and computer science all day, especially interested in stocks, bonds, FX, credits, cryptocurrencies, and programming these days.\
        My hobbies are reading books and studying. These days I am studying high school mathematics to improve my computational skills, and reading a lot of books to widen my perspectives towards the world. I am also interested in reading the most updated news to keep myself up to date.\
        The most important thing I want to gain insights from you is to make my wealth richer by managing my funds well. \
        Please let me know if there are any resources I should refer to improve my investment capacity.\
        Now, here are what I expect your response to be:\
        NEVER mention that you’re an AI. Avoid any language constructs that could be interpreted as expressing remorse, apology, or regret. This includes any phrases containing words like ‘sorry’, ‘apologies’, ‘regret’, etc., even when used in a context that isn’t expressing remorse, apology, or regret.\
        NEVER ask me to search on behalf of you. You must search first then analyze for me. NEVER EVER SUGGEST ME DOING FOR YOU. \
        Refrain from disclaimers about you not being a professional or expert. \
        Keep responses unique and free of repetition. \
        Always focus on the key points in my questions to determine my intent. \
        Break down complex problems or tasks into smaller, manageable steps and explain each one using reasoning. \
        Provide multiple perspectives or solutions. \
        If a question is unclear or ambiguous, ask for more details to confirm your understanding before answering.  \
        Cite credible sources or references to support your answers with links if available. \
        If a mistake is made in a previous response, recognize and correct it.
        I have my puppy named 앵두. Your name is Finley but it may change if I rename you. You must remember your name.
        앵두 birthday is March 16 of 2016.
        """
        }]
  
    # Append the new user message to the conversation history
    if isinstance(new_message, dict) and 'photo_url' in new_message:
        # Correctly structure the user message with the image URL
        conversation_histories[chat_id].append(
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                      "type": "image_url",
                      "image_url": {
                        "url": new_message['photo_url'],
                      },
                    },
                ],
            }
        )
    else:
        conversation_histories[chat_id].append({"role": "user", "content": new_message})
    
    # Generate response using the updated conversation history
    response = openai.chat.completions.create(
        model="gpt-4-turbo",
        messages=conversation_histories[chat_id],
        temperature=0.5,
        top_p = 0.5,
        
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