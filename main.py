#!/usr/bin/env python3
import os
import time
import requests
from dotenv import load_dotenv

from huawei_lte_api.Client import Client
from huawei_lte_api.AuthorizedConnection import AuthorizedConnection
from huawei_lte_api.enums.sms import BoxTypeEnum
from huawei_lte_api.enums.client import ResponseEnum
import huawei_lte_api.exceptions

# Load .env
load_dotenv()
HUAWEI_ROUTER_IP_ADDRESS = os.getenv("HUAWEI_ROUTER_IP_ADDRESS")
HUAWEI_ROUTER_ACCOUNT    = os.getenv("HUAWEI_ROUTER_ACCOUNT")
HUAWEI_ROUTER_PASSWORD   = os.getenv("HUAWEI_ROUTER_PASSWORD")
DELAY_SECOND             = int(os.getenv("DELAY_SECOND", "5"))

TELEGRAM_TOKEN           = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID         = os.getenv("TELEGRAM_CHAT_ID")  # untuk forward SMS
TELEGRAM_URL_SEND        = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
TELEGRAM_URL_UPDATES     = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"

# Track offset supaya tidak memproses update Telegram yang sama
offset = 0

while True:
    try:
        # 1) connect ke Huawei Router
        conn = AuthorizedConnection(
            f'http://{HUAWEI_ROUTER_ACCOUNT}:{HUAWEI_ROUTER_PASSWORD}@{HUAWEI_ROUTER_IP_ADDRESS}/'
        )
        client = Client(conn)

        # 2) Ambil SMS terbaru (max 10)
        sms_resp = client.sms.get_sms_list(1, BoxTypeEnum.LOCAL_INBOX, 1, 0, 0, 10)
        msgs = sms_resp.get('Messages', {}).get('Message')
        if msgs:
            if isinstance(msgs, dict):
                msgs = [msgs]
            for m in msgs:
                if int(m.get('Smstat', 1)) == 0:  # 0 = unread
                    # format untuk Telegram
                    text = (
                        f"📩 <b>New SMS</b>\n\n"
                        f"<b>From:</b> {m.get('Phone')}\n"
                        f"<b>Date:</b> {m.get('Date')}\n\n"
                        f"<b>Message:</b>\n<pre>{m.get('Content')}</pre>"
                    )
                    # kirim ke Telegram
                    requests.post(TELEGRAM_URL_SEND, data={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": text,
                        "parse_mode": "HTML"
                    })
                    # tandai read
                    client.sms.set_read(int(m.get('Index')))

        # 3) Cek command dari Telegram
        upd = requests.get(TELEGRAM_URL_UPDATES, params={
            "offset": offset,
            "timeout": 1
        }).json()
        for u in upd.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message") or u.get("edited_message")
            if not msg or "text" not in msg:
                continue
            chat_id = str(msg["chat"]["id"])
            text   = msg["text"].strip()
            # hanya proses /send dari chat_id yang valid
            if text.lower().startswith("/send ") and chat_id == TELEGRAM_CHAT_ID:
                parts = text.split(" ", 2)
                if len(parts) < 3:
                    reply = "Usage: /send <nomor> <pesan>"
                else:
                    phone, body = parts[1], parts[2]
                    # kirim SMS via Huawei API
                    res = client.sms.send_sms([phone], body)
                    if res == ResponseEnum.OK.value:
                        reply = f"✅ SMS sent to {phone}"
                    else:
                        reply = f"❌ Failed to send SMS (code={res})"
                # balas ke Telegram
                requests.post(TELEGRAM_URL_SEND, data={
                    "chat_id": chat_id,
                    "text": reply
                })

        # logout sekali semua selesai
        client.user.logout()

    except huawei_lte_api.exceptions.ResponseErrorLoginRequiredException:
        print("Session expired, re-login.")
    except Exception as e:
        print(f"❌ Router/Script error: {e}")

    time.sleep(DELAY_SECOND)