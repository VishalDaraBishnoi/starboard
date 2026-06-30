# Discord Starboard Bot

A simple Discord bot that posts starred messages to a starboard channel.

## Features

* Star reaction tracking
* Auto-post to starboard
* No duplicate posts
* Configurable threshold

## Setup

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Edit `.env` and fill in your values:

```
DISCORD_TOKEN=your_token
STARBOARD_CHANNEL_ID=channel_id
STAR_THRESHOLD=3
```

## Install & Run

```bash
pip install -r requirements.txt
python main.py
```

## Requirements

* Enable MESSAGE CONTENT INTENT
* Give bot: Send Messages, Embed Links, Read History
