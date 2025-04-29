from flask import Flask, request
import requests
import openai

app = Flask(__name__)

# Токенуудыг энд оруулна уу
PAGE_ACCESS_TOKEN = "ТАНЫ_FACEBOOK_PAGE_ACCESS_TOKEN"
VERIFY_TOKEN = "MINIBOT123"
OPENAI_API_KEY = "ТАНЫ_OPENAI_API_KEY"

openai.api_key = OPENAI_API_KEY

# GPT функц
def get_gpt_response(user_input):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Чи ухаалаг chatbot. Хэрэглэгчийн асуултад Монгол хэл дээр ойлгомжтой, товч хариулт өг."},
            {"role": "user", "content": user_input}
        ]
    )
    return response['choices'][0]['message']['content']

# Хэрэглэгчид хариу илгээх функц
def send_message(recipient_id, message_text):
    url = 'https://graph.facebook.com/v17.0/me/messages'
    headers = {'Content-Type': 'application/json'}
    payload = {
        'recipient': {'id': recipient_id},
        'message': {'text': message_text},
        'messaging_type': 'RESPONSE',
        'access_token': PAGE_ACCESS_TOKEN
    }
    requests.post(url, headers=headers, json=payload)

# Webhook баталгаажуулалт
@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Invalid verification token"

# Мессеж хүлээн авч GPT-р хариулах
@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    for entry in data.get('entry', []):
        for messaging in entry.get('messaging', []):
            sender_id = messaging['sender']['id']
            if 'message' in messaging and 'text' in messaging['message']:
                user_message = messaging['message']['text']
                bot_reply = get_gpt_response(user_message)
                send_message(sender_id, bot_reply)
    return "ok"

if __name__ == '__main__':
    app.run(debug=True)
