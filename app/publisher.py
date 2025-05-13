import requests
from flask import current_app
import os

def send_to_telegram(text, image_path=None):
    token = current_app.config['TELEGRAM_TOKEN']
    chat_id = current_app.config['TELEGRAM_CHAT_ID']

    try:
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendPhoto",
                    data={'chat_id': chat_id},
                    files={'photo': photo}
                )

        if text:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                data={'chat_id': chat_id, 'text': text[:3500]}
            )

    except Exception as e:
        print(f"[!] Ошибка отправки в Telegram: {e}")
