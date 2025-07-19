import os
import time
import requests
from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.enums.sms import BoxTypeEnum
import huawei_lte_api.exceptions
from dotenv import load_dotenv

# Load .env
load_dotenv()
HUAWEI_ROUTER_IP_ADDRESS = os.getenv("HUAWEI_ROUTER_IP_ADDRESS")
HUAWEI_ROUTER_ACCOUNT = os.getenv("HUAWEI_ROUTER_ACCOUNT")
HUAWEI_ROUTER_PASSWORD = os.getenv("HUAWEI_ROUTER_PASSWORD")
DELAY_SECOND = int(os.getenv("DELAY_SECOND", "10"))

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

while True:
    try:
        # Connect to Huawei Router
        connection = AuthorizedConnection(f'http://{HUAWEI_ROUTER_ACCOUNT}:{HUAWEI_ROUTER_PASSWORD}@{HUAWEI_ROUTER_IP_ADDRESS}/')
        client = Client(connection)

        # Ambil SMS terbaru (prioritas unread)
        sms = client.sms.get_sms_list(1, BoxTypeEnum.LOCAL_INBOX, 1, 0, 0, 1)

        if sms['Messages'] is None:
            client.user.logout()
            time.sleep(DELAY_SECOND)
            continue

        message = sms['Messages']['Message']

        if int(message['Smstat']) == 1:  # Sudah dibaca
            client.user.logout()
            time.sleep(DELAY_SECOND)
            continue

        # Format pesan untuk Telegram
        text = (
            f"📩 <b>New SMS</b>\n\n"
            f"<b>From:</b> {message['Phone']}\n"
            f"<b>Date:</b> {message['Date']}\n\n"
            f"<b>Message:</b>\n<pre>{message['Content']}</pre>"
        )

        # Kirim ke Telegram
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(TELEGRAM_URL, data=payload)

        if response.status_code == 200:
            print(f"✅ SMS from {message['Phone']} forwarded to Telegram.")
            client.sms.set_read(int(message['Index']))
        else:
            print(f"❌ Failed to send to Telegram: {response.text}")

        client.user.logout()
    except huawei_lte_api.exceptions.ResponseErrorLoginRequiredException:
        print("Session expired, re-login.")
    except Exception as e:
        print(f"❌ Router connection failed: {e}")

    time.sleep(DELAY_SECOND)