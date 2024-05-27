import requests
import json
import time
from openai import OpenAI
import os



def obtener_Mensaje_whatsapp(message):
    if 'type' not in message:
        return 'mensaje no reconocido'

    typeMessage = message['type']
    if typeMessage == 'text':
        return message['text']['body']
    elif typeMessage == 'button':
        return message['button']['text']
    elif typeMessage == 'interactive':
        if message['interactive']['type'] == 'list_reply':
            return message['interactive']['list_reply']['title']
        elif message['interactive']['type'] == 'button_reply':
            return message['interactive']['button_reply']['title']
    return 'mensaje no procesado'

def enviar_Mensaje_whatsapp(data):
    try:
        whatsapp_token = 'EAAFJrzEyDc4BO0PNvzo1ZC3Gryok4XeUoZCYRSGtl3HeiWGbGHWlhNiw3PLGJuPZCKeDmB9FKwrYcpDShm78FIcqLyZB97tWDnYmZBzI6iduLFO6g9SqM4RLZC7cxkblwG1VLneZBZBsZBuzYxPwFHVkdQQZAIyfe52IVwpA5ZC1nvMLP0YZB8rgI4VGE1QCiKTiOx8m'
        whatsapp_url = 'https://graph.facebook.com/v19.0/312868241913454/messages'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + whatsapp_token
        }
        response = requests.post(whatsapp_url, headers=headers, data=data)
        if response.status_code == 200:
            return 'mensaje enviado', 200
        else:
            return 'error al enviar mensaje', response.status_code
    except Exception as e:
        return str(e), 403

def text_Message(number, text):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "text",
        "text": {
            "body": text
        }
    })
    return data

def buttonReply_Message(number, options, body, footer, sedd, messageId):
    buttons = []
    for i, option in enumerate(options):
        buttons.append({
            "type": "reply",
            "reply": {
                "id": sedd + "_btn_" + str(i+1),
                "title": option
            }
        })

    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {"buttons": buttons}
        }
    })
    return data

def listReply_Message(number, options, body, footer, sedd, messageId):
    rows = []
    for i, option in enumerate(options):
        rows.append({
            "id": sedd + "_row_" + str(i+1),
            "title": option,
            "description": ""
        })

    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "footer": {"text": footer},
            "action": {
                "button": "Ver Opciones",
                "sections": [{"title": "Secciones", "rows": rows}]
            }
        }
    })
    return data

def document_Message(number, url, caption, filename):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "document",
        "document": {
            "link": url,
            "caption": caption,
            "filename": filename
        }
    })
    return data

def sticker_Message(number, sticker_id):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "sticker",
        "sticker": {"id": sticker_id}
    })
    return data

def replyReaction_Message(number, messageId, emoji):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "reaction",
        "reaction": {
            "message_id": messageId,
            "emoji": emoji
        }
    })
    return data

def replyText_Message(number, messageId, text):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "context": {"message_id": messageId},
        "type": "text",
        "text": {"body": text}
    })
    return data

def markRead_Message(messageId):
    data = json.dumps({
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": messageId
    })
    return data
def generar_respuesta_google_cloud(texto_usuario, api_key):
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": texto_usuario
                    }
                ]
            }
        ]
    }

    json_payload = json.dumps(payload)

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': 'AIzaSyAE_aDeizgmj2QcpV6Ia-GCEABMA6xsPNk'
    }

    response = requests.post(url, headers=headers, data=json_payload)
    print(response)
    if response.status_code == 200:
        data = json.loads(response.text)
        return data['candidates'][0]['content']['parts'][0]['text'].strip()
    else:
        print("Error:", response.status_code)
        return None

def administrar_chatbot(text, number, messageId, name):
    key = os.environ.get("OPENAI_API_KEY")
    text = text.lower()
    list = []
    print("mensaje del usuario: ", text)

    markRead = markRead_Message(messageId)
    list.append(markRead)
    time.sleep(2)

    respuesta_ai = generar_respuesta_google_cloud(text, key)
    textMessage = text_Message(number, respuesta_ai)
    list.append(textMessage)

    for item in list:
        enviar_Mensaje_whatsapp(item)

def replace_start(s):
    number = s[3:]
    if s.startswith("521"):
        return "52" + number
    elif s.startswith("549"):
        return "54" + number
    else:
        return s
