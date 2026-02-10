# ExampleBot

A simple Telegram bot built with Aiogram 3.x.

## Features

- User registration and profiles
- Balance management
- Admin statistics
- SQLite database support

## Requirements

- Python 3.10+
- pip

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   
   Fill in your credentials:
   - `BOT_TOKEN` - Your Telegram bot token
   - `ADMIN_IDS` - Comma-separated admin IDs
   - `CHANNEL_ID` - Channel ID for notifications
   - `CHANNEL_URL` - Channel URL

## Usage

Start the bot:
```bash
python -m bot
```

## Commands

### User Commands
- `/start` - Start the bot
- `/profile` - View your profile
- `/balance` - Check your balance
- `/help` - Show help

### Admin Commands
- `/admin_stats` - View database statistics
- `/admin_users` - List all users
- `/admin_help` - Admin help
