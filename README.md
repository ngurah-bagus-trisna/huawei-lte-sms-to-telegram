# Huawei LTE SMS To Telegram

Huawei SMS to Telegram Bot

This bot connects to a Huawei LTE router, forwards incoming SMS messages to a Telegram chat, and allows you to send SMS from Telegram.

Thanks to @Salamaek to create API for Huawei LAN/WAN Modems, you can visit repository below

- https://github.com/Salamek/huawei-lte-api

⸻

> Testing on huawei e8372

Prerequisites
	•	Python 3.11+ installed on your system
	•	Docker (optional, for containerized deployment)
	•	A Huawei LTE router with SMS API enabled (e.g., most Huawei MiFi or LTE routers)
	•	A Telegram Bot token and a chat ID where the bot will post and accept commands

## Setup

1.	Clone this repository

```
git clone https://github.com/yourusername/huawei-sms-bot.git
cd huawei-sms-bot
```

2.	Copy and edit the .env file

```
cp .env.example .env
```

Fill in your router credentials and Telegram bot settings:

```
# .env
HUAWEI_ROUTER_IP_ADDRESS=192.168.8.1
HUAWEI_ROUTER_ACCOUNT=admin
HUAWEI_ROUTER_PASSWORD=your_password
DELAY_SECOND=5            # Polling interval in seconds

TELEGRAM_TOKEN=
TELEGRAM_CHAT_ID=
```

3.	Create a Python virtual environment and install dependencies

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Running Locally

With the environment ready, simply run:

python huawei_sms_to_telegram.py

The script will:

1.	Poll your Huawei router’s SMS inbox and forward unread SMS to Telegram.

2.	Listen for /send <number> <message> commands in Telegram and send SMS via the router API.

Docker Image

You can run the bot in a Docker container as follows:

1.	Build the container

```
docker build -t huawei-sms-bot .
```

2. **Run the container**

```
docker run -d \
  --name huawei-sms-bot \
  -v $(pwd)/.env:/app/.env:ro \
  --env-file .env \
  huawei-sms-bot

```

## GitHub Actions (GHCR Publishing)

A CI workflow (`.github/workflows/ghcr-publish.yml`) is provided to build and push the Docker image to GitHub Container Registry (ghcr.io) on every push to `main`:

- Tags the image as `latest` and by commit SHA.

Ensure `GITHUB_TOKEN` has write permissions for `packages` in your repo settings.

