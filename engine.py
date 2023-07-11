from config import token, ownerId, testerIds, prefix, prefixActive, botName
from transformers import pipeline
from googletrans import Translator
import websocket
import threading
import requests
import json
import time
import os

os.system("cls")
translator = Translator()

generator = pipeline(
    'text-generation',
    model="gpt2",
    pad_token_id=0,
    eos_token_id=50256
)


def translate_tr(text):
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, dest='tr')
    return translation.text


def translate_en(text):
    translator = Translator(service_urls=['translate.google.com'])
    translation = translator.translate(text, dest='en')
    return translation.text


def directChannelMessage(url, message):
    payload2 = {
        "content": message
    }

    header = {
        "authorization": token
    }

    r = requests.post(url=url, data=payload2, headers=header)


def send_json_request(ws, request):
    ws.send(json.dumps(request))


def recieve_json_response(ws):
    response = ws.recv()
    if response:
        return json.loads(response)


def heartbeat(interval, ws):
    print(f'{botName}: Dinleme Başladı')

    while True:
        time.sleep(interval)
        heartbeatJSON = {
            "op": 1,
            "d": "null"
        }

        send_json_request(ws, heartbeatJSON)
        print("Sairus: Dinleme Gönderildi")


def gpt2():
    if content.startswith(prefix):
        if id == ownerId or id in testerIds:
            fixedContent = content.replace("sairus ", "")
            translatedContent = translate_en(fixedContent)
            res = generator(translatedContent, do_sample=True,
                            min_length=50, max_new_tokens=100, temperature=0.5)
            result_fixed = res[0]['generated_text']
            turkish_translation = translate_tr(result_fixed)
            directChannelMessage(
                url=url, message=f"{botName} Chat: {turkish_translation}")


ws = websocket.WebSocket()
ws.connect('wss://gateway.discord.gg/?v=6&encording=json')
event = recieve_json_response(ws)

heartbeat_interval = event['d']['heartbeat_interval'] / 1000
threading._start_new_thread(heartbeat, (heartbeat_interval, ws))

payload = {
    "op": 2,
    "d": {
        "token": token,
        "properties": {
            "$os": "windows",
            "$browser": "edge",
            "$device": "pc"
        }
    }
}

send_json_request(ws, payload)

while True:
    event = recieve_json_response(ws)

    try:
        global content
        global id
        global channelId
        global username

        id = int(event['d']['author']['id'])
        username = str(event['d']['author']['username'])
        channelId = event['d']['channel_id']
        content = str(event['d']['content'])
        url = f"https://discord.com/api/v9/channels/{channelId}/messages"

        # Kod Yazma Alanı

        gpt2()
    except:
        pass
